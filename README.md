
Swarming
===
`docker stack deploy admiral --compose-file docker-compose.yml`

If you need no more than one replica of each service you can start the composition with:

`docker-compose up`

- Celery Flower:   http://localhost:5555
- Mongo Express:   http://localhost:8081
- Redis Commander: http://localhost:8082


Debugging Tips
===

To get a shell in a running container:

`docker-compose exec admiral /bin/sh`

To get a shell in a stopped or crashed container:

`docker run -it --rm --entrypoint=sh admiral`

Current debugging stuff
```
docker-compose exec admiral admiral -i
from admiral.port_scan.tasks import *
from admiral.certs.tasks import *
summary = summary_by_domain.delay('cyber.dhs.gov')
id = summary.wait()[0]['min_cert_id']
first_cert = cert_by_id.delay(id)
ns1 = up_scan.delay('10.28.20.200')
ns2 = port_scan.delay('10.28.20.200')
a.backend.get(a.backend.get_key_for_task(a.id))
```


Celery Magic
===
Get a result later:
```
In [23]: res = AsyncResult('7b1f10ae-fddc-4a79-9afc-4aaafb18623f')                                                                                            
In [24]: res.get()                   
Out[24]: 11
```

TODO
====
* Make a shared task module -or-
  * make using send_task easy, or signatures
  * http://docs.celeryproject.org/en/latest/reference/celery.html#celery.Celery.send_task
  * http://docs.celeryproject.org/en/latest/reference/celery.html#celery.signature
* The interactive mode is really what we want for a work producer
* The non-interactive mode is our worker configuration
* set task_send_sent_event for monitoring (added.)
* monitor events and make a super sexy display
