from gevent import monkey
monkey.patch_all()

#core imports
import datetime
#framework imports
import gevent
import redis
#app imports
from utils import display_time


def get_stats(host='',port='',passwd=''):

    try:

        if passwd:
            conn = redis.StrictRedis(host=host, port=port, password=passwd)
        else:
            conn = redis.StrictRedis(host=host, port=port)

        return conn.info()
    except Exception as e:
        print e
        return None


def get_raw_results(active_servers):

    if active_servers:

        workers = [gevent.spawn(get_stats,host=item.server.value,port=item.port.value,passwd=item.authentication.value['pswd']) for item in active_servers]
        gevent.joinall(workers,timeout=30)

    return workers


def redis_get_panel_results(active_servers):

    stats = []
    
    if active_servers:

        workers = get_raw_results(active_servers)

        for index,item in enumerate(active_servers):

            redis_stats = workers[index].value

            if redis_stats:
                stats.append({
                            "status":"success",
                            "server":item.server.value+":"+str(item.port.value),
                            "uptime":display_time(int(redis_stats['uptime_in_seconds']))
                            })
            else:
                stats.append({
                            "status":"danger",
                            "server":item.server.value+":"+str(item.port.value),
                            "uptime":''
                            })

            item.last_check.value = datetime.datetime.now()
            item.save()

    return stats


def redis_get_datatable_results(active_servers):

    stats = []
    
    if active_servers:

        workers = get_raw_results(active_servers)

        for index,item in enumerate(active_servers):

            redis_stats = workers[index].value

            if redis_stats:
                stats.append([item.server.value+":"+str(item.port.value),item.service_type.value.upper(),display_time(int(redis_stats['uptime_in_seconds'])),""])
            else:
                stats.append([item.server.value+":"+str(item.port.value),item.service_type.value.upper(),'',"ERROR - cannot be reached"])

            item.last_check.value = datetime.datetime.now()
            item.save()

    output = {}
    output['data'] = stats
    output['recordsTotal'] = len(stats)
    output['recordsFiltered'] = len(stats)

    return output