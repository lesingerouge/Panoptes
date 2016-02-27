from mongo import mongo_get_panel_results, mongo_get_datatable_results
from otherdb import redis_get_panel_results, redis_get_datatable_results


REGISTERED_SERVICES = {
    "mongo":{"panel":mongo_get_panel_results,
             "datatable":mongo_get_datatable_results},
    "redis":{"panel":redis_get_panel_results,
             "datatable":redis_get_datatable_results}
}
