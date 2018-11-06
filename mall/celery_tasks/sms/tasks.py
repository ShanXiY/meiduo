
"""
1.任务
    任务的文件名必须是tasks
2.broker
3.worker

"""
from libs.yuntongxun.sms import CCP
from celery_tasks.main import app


@app.task
def send_sms_code(mobile,sms_code):
    CCP().send_template_sms(mobile,[sms_code,5],1)

