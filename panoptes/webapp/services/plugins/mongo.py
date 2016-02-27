from gevent import monkey
monkey.patch_all()

#core imports
import datetime
#framework imports
import gevent
from pymongo import MongoClient
#app imports
from utils import display_time


def get_stats(host='localhost',port=27017,authenticatedb=None,username=None,passwd=None,action=''):

    try:
        tempdb = MongoClient(host=host,port=int(port))
        if authenticatedb:
            tempdb[authenticatedb].authenticate(username,passwd)

        return tempdb.admin.command(action)
    except Exception as e:
        print e
        return None


def get_raw_results(active_servers):

    if active_servers:

        workers = []

        for item in active_servers:
            if item.authentication.value['db']:
                action = "replSetGetStatus"
            else:
                action = "serverStatus"

            workers.append(gevent.spawn(get_stats,host=item.server.value,port=item.port.value,authenticatedb=item.authentication.value['db'],username=item.authentication.value['user'],passwd=item.authentication.value['pswd'],action=action))

        gevent.joinall(workers,timeout=5)
        
    return workers


def mongo_get_panel_results(active_servers):

    stats = []
        
    if active_servers:

        workers = get_raw_results(active_servers)

        for index,item in enumerate(active_servers):
            

            mongo_stats = workers[index].value

            if item.authentication.value['db'] and mongo_stats:

                current_server = [x for x in mongo_stats['members'] if x.get("self")][0]
                members = [str(x['name']) for x in mongo_stats['members'] if not x.get("self")]
                member_status = [str(int(x['health'])) for x in mongo_stats['members'] if not x.get("self")]
                member_states = [x['stateStr'] for x in mongo_stats['members'] if not x.get("self")]

                stats.append({
                        "status":"success" if current_server['health'] else "error",
                        "server":item.server.value+":"+str(item.port.value),
                        "uptime":display_time(int(current_server['uptime'])),
                        "replicaset":True,
                        "replicaset_name":mongo_stats['set'],
                        "repl_status":current_server['stateStr'],
                        "repl_members":members,
                        "repl_members_status":member_status,
                        "repl_members_states":member_states
                        })
        
            elif mongo_stats:
                stats.append({
                        "status":"success",
                        "server":item.server.value+" : "+str(item.port.value),
                        "uptime":display_time(int(mongo_stats['uptime'])),
                        "replicaset":False,
                        "mem":mongo_stats['mem']
                        })
            else:
                stats.append({
                        "status":"danger",
                        "replicaset":False,
                        "server":item.server.value+" : "+str(item.port.value),
                        "mem":'',
                        "uptime":''
                        })

            item.last_check.value = datetime.datetime.now()
            item.save()

    replicasets = {}
    simpledbs = []
    for item in stats:
        if item['replicaset']:
            replica_id = item['repl_members'] + [str(item['server'])]
            replica_id = str(sorted(replica_id))
            if replica_id in replicasets:
                replicasets[replica_id].append(item)
            else:
                replicasets[replica_id] = [item]
        else:
            simpledbs.append(item)

    output = []
    for x in replicasets:
        output.append({"replicaset":True,"replicaset_name":replicasets[x][0]['replicaset_name'],"members":replicasets[x]})

    output.extend(simpledbs)

    return output


def mongo_get_datatable_results(active_servers):

    stats = []

    if active_servers:

        workers = get_raw_results(active_servers)

        for index,item in enumerate(active_servers):
            
            mongo_stats = workers[index].value

            if item.authentication.value['db'] and mongo_stats:

                current_set = mongo_stats['set']
                current_server = [x for x in mongo_stats['members'] if x.get("self")][0]

                stats.append([item.server.value+":"+str(item.port.value),item.service_type.value.upper(),display_time(int(current_server['uptime'])),current_set+ "-" +current_server['stateStr']])

            elif mongo_stats:
                stats.append([item.server.value+":"+str(item.port.value),item.service_type.value.upper(),display_time(int(mongo_stats['uptime'])),''])

            else:
                stats.append([item.server.value+":"+str(item.port.value),item.service_type.value.upper(),'',"ERROR - cannot be reached"])

            item.last_check.value = datetime.datetime.now()
            item.save()

    output = {}
    output['data'] = stats
    output['recordsTotal'] = len(stats)
    output['recordsFiltered'] = len(stats)

    return output