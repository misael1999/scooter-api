from scooter.utils.functions import send_mail_verification, generate_verification_token
# Celery
from celery.task import task


@task(name='send_email_task', max_retries=3)
def send_email_task(subject, to_user, path_template, data):
    """ Send email in background """
    send_mail_verification(subject, to_user, path_template, data)
