import csv
import time
import sys
from datetime import  datetime

start_time = time.time()
write_threshold = 1000
header_row = []

V = {
  'SSL_3_0':            0x0300,
  'TLS_1_0':            0x0301,
  'TLS_1_1':            0x0302,
  'TLS_1_2':            0x0303,
  'TLS_1_3':            0x0304,

  'TLS_1_3_DRAFT0':     0x7f00,
  'TLS_1_3_DRAFT1':     0x7f01,
  'TLS_1_3_DRAFT2':     0x7f02,
  'TLS_1_3_DRAFT3':     0x7f03,
  'TLS_1_3_DRAFT4':     0x7f04,
  'TLS_1_3_DRAFT5':     0x7f05,
  'TLS_1_3_DRAFT6':     0x7f06,
  'TLS_1_3_DRAFT7':     0x7f07,
  'TLS_1_3_DRAFT8':     0x7f08,
  'TLS_1_3_DRAFT9':     0x7f09,
  'TLS_1_3_DRAFT10':    0x7f0a,
  'TLS_1_3_DRAFT11':    0x7f0b,
  'TLS_1_3_DRAFT12':    0x7f0c,
  'TLS_1_3_DRAFT13':    0x7f0d,
  'TLS_1_3_DRAFT14':    0x7f0e,
  'TLS_1_3_DRAFT15':    0x7f0f,
  'TLS_1_3_DRAFT16':    0x7f10,
  'TLS_1_3_DRAFT17':    0x7f11,
  'TLS_1_3_DRAFT18':    0x7f12,
  'TLS_1_3_DRAFT19':    0x7f13,
  'TLS_1_3_DRAFT20':    0x7f14,
  'TLS_1_3_DRAFT21':    0x7f15,
  'TLS_1_3_DRAFT22':    0x7f16,
  'TLS_1_3_DRAFT23':    0x7f17,
  'TLS_1_3_DRAFT24':    0x7f18,
  'TLS_1_3_DRAFT25':    0x7f19,
  'TLS_1_3_DRAFT26':    0x7f1a,
  'TLS_1_3_DRAFT27':    0x7f1b,
  'TLS_1_3_DRAFT28':    0x7f1c,
  'TLS_1_3_FB20':       0xfb14,
  'TLS_1_3_FB21':       0xfb15,
  'TLS_1_3_FB22':       0xfb16,
  'TLS_1_3_FB23':       0xfb17,
  'TLS_1_3_FB26':       0xfb1a,
  'TLS_1_3_FB40':       0xfb28,
  'DTLS_1_0':           0xfeff,
  'DTLS_1_1':           0xfefd,
  'TLS_1_3_7E01':       0x7e01,
  'TLS_1_3_7E02':       0x7e02,
  'TLS_1_3_7E03':       0x7e03,
  'TLS_1_3_7A12':       0x7a12
}

V_i = {y:x for (x,y) in V.items()}

lowest_date = ''
highest_date = ''
low_tls_versions_temporal = {}
high_tls_versions_temporal = {}
supported_versions_temporal = {}
final_versions_temporal = {}
server_tls_versions_temporal = {}
server_downgrade_markers_temporal = {}
server_hello_retry_request_temporal = {}
total_records_temporal = {}
total_ports = []
tlsv13_total_ports = []
FB_apps = []

def date_lower(a, b):
  if int(a.replace('-','')) < int(b.replace('-', '')):
    return True
  return False

def date_range(a, b):
  start_year = int(a.split('-')[0])
  start_month = int(a.split('-')[1])
  end_year = int(b.split('-')[0])
  end_month = int(b.split('-')[1])

  results = []
  month = start_month
  year = start_year
  results.append(a)
  while ((month == end_month and year == end_year) is not True):
    if month == 12:
      month = 0
      year += 1
    month += 1
    results.append('%d-%02d' % (year, month))

  return results

with open(sys.argv[1], 'rU') as csvfile:
  csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
  row_num = 0
  for row in csvreader:
    try:
      row_num += 1
      if header_row == []:
        header_row = row
        continue
      dictionary = dict(zip(header_row, row))
      flow_time = dictionary['flow_time']
      flow_time = datetime.strptime(flow_time, '%Y-%m-%d %H:%M:%S')
      if flow_time.year < 2015 or flow_time.year > 2019:
        sys.stderr.write('\nweird date found: %s\n' % (flow_time))
        continue
      time_key = "%d-%02d" % (flow_time.year, flow_time.month)
      if lowest_date == '':
        lowest_date = time_key
        highest_date = time_key

      if time_key not in total_records_temporal:
        total_records_temporal[time_key] = {'snis': [], 'snis_v13': [], 'snis_negotiated': [], 'app_packages': [], 'records': 0}

      if time_key not in final_versions_temporal:
        final_versions_temporal[time_key] = {'total': 0, 'TLSv1.3-ALL': 0}

      if time_key not in supported_versions_temporal:
        supported_versions_temporal[time_key] = {'total': 0, 'app_packages': []}

      if time_key not in server_downgrade_markers_temporal:
        server_downgrade_markers_temporal[time_key] = { 'tlsv10': [], 'tlsv12': [] }

        try:
          if date_lower(time_key, lowest_date):
            lowest_date = time_key
          if date_lower(highest_date, time_key):
            highest_date = time_key
        except Exception as e:
          sys.stderr.write('Error comparing dates: %s %s %s\n' % (lowest_date, highest_date,time_key))
          sys.exit(1)
      total_records_temporal[time_key]['records'] += 1

      if dictionary['dst_port'] not in total_ports:
        total_ports.append(dictionary['dst_port'])

      if dictionary['sni'] not in total_records_temporal[time_key]['snis']:
        total_records_temporal[time_key]['snis'].append(dictionary['sni'])

      if dictionary['app_package'] not in total_records_temporal[time_key]['app_packages']:
        total_records_temporal[time_key]['app_packages'].append(dictionary['app_package'])

      server_supports_tlsv13 = 0
      if dictionary['server-downgrade-marker'] not in ['', 'none']:
        server_supports_tlsv13 = 1
        if dictionary['sni'] not in server_downgrade_markers_temporal[time_key][dictionary['server-downgrade-marker']]:
          server_downgrade_markers_temporal[time_key][dictionary['server-downgrade-marker']].append(dictionary['sni'])
      if dictionary['server-hello-retry-request'] not in ['', '0']:
        server_supports_tlsv13 = 1
        pass

      if dictionary['client-supported-versions'] != '':
        highest_version = V_i[int(dictionary['client-supported-versions'].split(',')[0].replace('unknown (','').replace(')',''))]
        if highest_version not in supported_versions_temporal[time_key]:
          supported_versions_temporal[time_key][highest_version] = 0
        supported_versions_temporal[time_key][highest_version] += 1
        supported_versions_temporal[time_key]['total'] += 1
        if dictionary['app_package'] not in supported_versions_temporal[time_key]['app_packages']:
          supported_versions_temporal[time_key]['app_packages'].append(dictionary['app_package'])
        if dictionary['dst_port'] not in tlsv13_total_ports:
          tlsv13_total_ports.append(dictionary['dst_port'])

      if dictionary['resulting-version(=max server_version,supported_version)'] != '':
        final_version = V_i[int(dictionary['resulting-version(=max server_version,supported_version)'].split(',')[0].replace('unknown (','').replace(')',''))]
        if 'TLS_1_3' in final_version:
          server_supports_tlsv13 = 1
          final_versions_temporal[time_key]['TLSv1.3-ALL'] += 1
        if final_version not in final_versions_temporal[time_key]:
          final_versions_temporal[time_key][final_version] = 0
        final_versions_temporal[time_key][final_version] += 1
        final_versions_temporal[time_key]['total'] += 1
        if dictionary['sni'] not in total_records_temporal[time_key]['snis_negotiated']:
           total_records_temporal[time_key]['snis_negotiated'].append(dictionary['sni'])
      if server_supports_tlsv13 and dictionary['sni'] not in total_records_temporal[time_key]['snis_v13']:
        total_records_temporal[time_key]['snis_v13'].append(dictionary['sni'])

      if row_num % write_threshold == 0:
        elapsed = time.time() - start_time
        rate = row_num / elapsed
        print '%d (%f records/second)\r' % (row_num, rate),
    except Exception as e:
      sys.stderr.write('Error in line %d: %s\n' % (row_num, e))
    except KeyboardInterrupt:
      sys.stderr.write('Interrupted, finishing off...\n')
      break


downgrade_markers_temporal_file = open('downgrade_markers_temporal.csv', 'w')
downgrade_markers_temporal_file.write('Month,Version,Percentage\n')
server_support_for_tlsv13_temporal_file = open('servers_supporting_tlsv13_temporal.csv', 'w')
server_support_for_tlsv13_temporal_file.write('Month,Percentage,Count\n')
client_support_for_tlsv13_temporal_file = open('clients_supporting_tlsv13_temporal.csv', 'w')
client_support_for_tlsv13_temporal_file.write('Month,AppPercentage,Apps,ClientHelloPercentage,ClientHellos\n')
advertised_tlsv13_version_breakdown_temporal_file = open('advertised_tlsv13_version_breakdown_temporal.csv', 'w')
advertised_tlsv13_version_breakdown_temporal_file.write('Month,Version,Percentage,Count\n')
negotiated_tls_version_breakdown_temporal_file = open('negotiated_tls_version_breakdown_temporal.csv', 'w')
negotiated_tls_version_breakdown_temporal_file.write('Month,Version,Percentage,Count\n')
negotiated_tlsv13_version_breakdown_temporal_file = open('negotiated_tlsv13_version_breakdown_temporal.csv', 'w')
negotiated_tlsv13_version_breakdown_temporal_file.write('Month,Version,Percentage,Count\n')
all_tlsv13_apps = open('all_tlsv13_apps.csv', 'w')
all_tlsv13_apps.write('Month,App\n')

total_packages = []
total_snis = []
for time_key in date_range(lowest_date, highest_date):
  print time_key
  for sni in total_records_temporal[time_key]['snis']:
    if sni not in total_snis:
      total_snis.append(sni)
  
  for package in total_records_temporal[time_key]['app_packages']:
    if package not in total_packages:
      total_packages.append(package)

  print '\tservers_with_downgrade_markers\n\t*************'
  if time_key not in server_downgrade_markers_temporal:
    print '\tno downgrade markers'
    downgrade_markers_temporal_file.write('%s-01,TLSv1.0 or TLSv1.1,0\n' % (time_key))
    downgrade_markers_temporal_file.write('%s-01,TLSv1.2,0\n' % (time_key))
  else:
    
    if final_versions_temporal[time_key]['total'] != 0:
      percentage_of_negotiated_tls_connections_downgraded_to_tlsv10 = (float(len(server_downgrade_markers_temporal[time_key]['tlsv10'])) / float(final_versions_temporal[time_key]['total'])) * 100
      percentage_of_negotiated_tls_connections_downgraded_to_tlsv12 = (float(len(server_downgrade_markers_temporal[time_key]['tlsv12'])) / float(final_versions_temporal[time_key]['total'])) * 100
    else:
      percentage_of_negotiated_tls_connections_downgraded_to_tlsv10 = 0
      percentage_of_negotiated_tls_connections_downgraded_to_tlsv12 = 0
    
    print '\tpercentage of servers downgraded to tlsv10'
    print '\t%f%%' % percentage_of_negotiated_tls_connections_downgraded_to_tlsv10
    
    print '\tpercentage of servers downgraded to tlsv12'
    print '\t%f%%' % percentage_of_negotiated_tls_connections_downgraded_to_tlsv12
    downgrade_markers_temporal_file.write('%s-01,TLSv1.0 or TLSv1.1,%f\n' % (time_key, percentage_of_negotiated_tls_connections_downgraded_to_tlsv10))
    downgrade_markers_temporal_file.write('%s-01,TLSv1.2,%f\n' % (time_key, percentage_of_negotiated_tls_connections_downgraded_to_tlsv12))
    print '\t*********'
  print '\tpercentage of servers supporting tlsv13'
  
  if final_versions_temporal[time_key]['total'] != 0:
    percentage_of_servers_supporting_tlsv13 = (float(len(total_records_temporal[time_key]['snis_v13'])) / float(len(total_records_temporal[time_key]['snis_negotiated']))) * 100
  else:
    percentage_of_servers_supporting_tlsv13 = 0

  print '\t%f%%' % percentage_of_servers_supporting_tlsv13
  server_support_for_tlsv13_temporal_file.write('%s-01,%f,%d\n' % (time_key, percentage_of_servers_supporting_tlsv13, len(total_records_temporal[time_key]['snis_v13'])))
  print '\t*********'
  print '\tclient_hellos_with_supported_versions\n\t*************'
  if time_key not in supported_versions_temporal:
    print '\tno TLSv1.3 client hellos with supported versions'
    pass
  else:
    for app in supported_versions_temporal[time_key]['app_packages']:
      all_tlsv13_apps.write('%s-01,%s\n' % (time_key, app))

    for version, connection_count in supported_versions_temporal[time_key].items():
      if version == 'total':
        continue
      if version == 'app_packages':
        continue

      client_hellos_with_supported_versions_percentage = (float(connection_count) / float(supported_versions_temporal[time_key]['total'])) * 100
      print '\t%s %f%%' % (version, client_hellos_with_supported_versions_percentage)
      advertised_tlsv13_version_breakdown_temporal_file.write('%s-01,%s,%f,%d\n' % (time_key,version,client_hellos_with_supported_versions_percentage,connection_count))      
    print '\ttotal TLSv1.3 client hellos: %d' % (supported_versions_temporal[time_key]['total'])
    percentage_packages_supporting_tlsv13 = (float(len(supported_versions_temporal[time_key]['app_packages'])) / float(len(total_records_temporal[time_key]['app_packages']))) * 100
    print '\tpercentage of packages supporting TLSv1.3: %f%%' % (percentage_packages_supporting_tlsv13)
    percentage_client_hellos_supporting_tlsv13 = (float(supported_versions_temporal[time_key]['total']) / float(total_records_temporal[time_key]['records'])) * 100
    client_support_for_tlsv13_temporal_file.write('%s-01,%f,%d,%f,%d\n' % (time_key,percentage_packages_supporting_tlsv13,len(supported_versions_temporal[time_key]['app_packages']),percentage_client_hellos_supporting_tlsv13,supported_versions_temporal[time_key]['total']))
  print '\t*********'
  print '\tnegotiated_connection_versions\n\t*************'
  if time_key not in final_versions_temporal:
    print '\tno negotiated TLS connections'
    pass
  else:
    for version, connection_count in final_versions_temporal[time_key].items():
      if version == 'total':
        continue
      print version
      if 'TLS_1_3' in version and version != 'TLSv1.3-ALL':
        negotiated_tlsv13_version_percentage = (float(connection_count) / float(final_versions_temporal[time_key]['TLSv1.3-ALL'])) * 100
        print '\t%s %f%%' % (version, negotiated_tlsv13_version_percentage)
        negotiated_tlsv13_version_breakdown_temporal_file.write('%s-01,%s,%f,%d\n' % (time_key, version, negotiated_tlsv13_version_percentage, connection_count))
        continue

      if final_versions_temporal[time_key]['total'] != 0:
        negotiated_version_percentage = (float(connection_count) / float(final_versions_temporal[time_key]['total'])) * 100
      else:
        negotiated_version_percentage = 0

      print '\t%s %f%%' % (version, negotiated_version_percentage)
      negotiated_tls_version_breakdown_temporal_file.write('%s-01,%s,%f,%d\n' % (time_key, version, negotiated_version_percentage, connection_count))
    print '\ttotal negotiated TLS connections: %d' % (final_versions_temporal[time_key]['total'])
  print '\t*********'


print '***************************************'
print 'total packages: %d total snis: %d total_ports: %d tlsv13_total_ports: %d' % (len(total_packages), len(total_snis), len(total_ports), len(tlsv13_total_ports))

print 'Facebook apps: %d' % (len(FB_apps))
print '****************'
for app in FB_apps:
  print '\t%s' % app

  