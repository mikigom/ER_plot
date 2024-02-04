from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    host = "https://er-plot.xyz"  # 대상 웹사이트 주소
    wait_time = between(1, 10)  # 사용자의 행동 사이에 대기하는 시간

    @task
    def visit_main_page(self):
        self.client.get("/")  # 메인 페이지 방문
