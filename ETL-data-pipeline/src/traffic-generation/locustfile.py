from locust import HttpUser, task, between, constant
from locust import LoadTestShape
import pandas as pd



class HelloWorldUser(HttpUser):
    wait_time = constant(1)

    @task
    def hello_world(self):
        self.client.get('/hello')


class StagesShape(LoadTestShape):
    """
    A simply load test shape class that has different user and spawn_rate at
    different stages.
    Keyword arguments:
        stages -- A list of dicts, each representing a stage with the following keys:
            duration -- When #seconds passed, the test is advanced to the next stage
            users -- Total user count
            spawn_rate -- Number of users to start/stop per second
        stop_at_end -- Can be set to stop once all stages have run.
    """
    num_reqs = pd.read_csv('./num_reqs.csv')
    start = 10
    stages= []
    for i in num_reqs.num_reqs:
        d = [{"duration": start, "users": i, "spawn_rate": i}]
        stages.extend(d)
        start += 30
        

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
    