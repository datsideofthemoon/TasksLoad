import datetime
import httplib2, argparse
import os

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

def GetTasks():
    # CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret. You can see the Client ID
    # and Client secret on the APIs page in the Cloud Console:
    # <https://cloud.google.com/console#/project/440632827315/apiui>
    CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

    # Set up a Flow object to be used for authentication.
    # Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
    # NEED. For more information on using scopes please see
    # <https://developers.google.com/+/best-practices>.
    FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS, scope=['https://www.googleapis.com/auth/tasks',
                                                                 'https://www.googleapis.com/auth/tasks.readonly', ],
                                          message=tools.message_if_missing(CLIENT_SECRETS))
    # Parse the command-line
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                     parents=[tools.argparser])
    flags = parser.parse_args([])
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage(os.path.join(os.path.dirname(__file__), 'tasks.dat'))
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)
    # Construct the service object for the interacting with the Tasks API.
    service = discovery.build('tasks', 'v1', http=http)

    try:
        tasklists = service.tasklists().list().execute()
        mytasklistID = tasklists['items']
        mytasklistID = mytasklistID[0]
        mytasklistID = mytasklistID['id']
        tasks = service.tasks().list(tasklist=mytasklistID).execute()
        return tasks
    except client.AccessTokenRefreshError:
        print("The credentials have been revoked or expired.")
        return None

def SaveToFile(res):
    f = open(os.path.join(os.path.dirname(__file__), 'tasks.db'), 'w')
    f.write(res)
    f.close()

def SendBroadcastIntent(res,adr=None):
    #sys.path = ['', '/mnt/sdcard/sl4a/scripts', '/mnt/sdcard/com.googlecode.pythonforandroid/extras/python',
    #            '/data/data/com.googlecode.pythonforandroid/files/python/lib',
    #            '/data/data/com.googlecode.pythonforandroid/files/python/lib/python2.6/lib-dynload']
    import android
    activity = 'org.zooper.zw.action.TASKERVAR'
    bundlename = 'org.zooper.zw.tasker.var.extra.BUNDLE'
    extras = {'org.zooper.zw.tasker.var.extra.INT_VERSION_CODE':1, \
              'org.zooper.zw.tasker.var.extra.STRING_VAR':'NextTask', \
              'org.zooper.zw.tasker.var.extra.STRING_TEXT':res}
    bundle = {bundlename:extras}
    packagename = 'org.zooper.zw'
    if adr is not None:
        droid = android.Android(addr=adr)
    else:
        droid = android.Android()
    intent = droid.makeIntent(activity, None, None, bundle, None, packagename, None).result
    droid.sendBroadcastIntent(intent)

def main():
    tasks=GetTasks()
    if tasks is not None:
        res = ''
        already = False
        for item in tasks['items']:
            if item["status"] == "needsAction":
                date = item['updated']
                date = date[:-1]
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
                date = date + datetime.timedelta(hours=+4)
                date = datetime.datetime.strftime(date, "%d.%m %H:%M")
                if already:
                    res += '\n'
                res += date + ': ' + item['title']
                #print(date + ': ' + item['title'])
                already = True
        SendBroadcastIntent(res)
        #SendBroadcastIntent(res,['android-16c970ae09586dba', 7777])
        return True
    else:
        SendBroadcastIntent('[Authorization or other problem]')
        return False

if __name__ == "__main__":
    if main(): exit()