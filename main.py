from pyrogram import Client, Filters
import mimetypes,requests,os,re,time
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


try:
    import config
except ImportError:
    with open('config.py', "w") as the_file:
        tok = str(input("812132645:AAHAo1prXYco71Wf-uxtOGh3sKmzVC-ZkB0 / @Utube_UploaderBot  "))
        content = "TOKEN = '"+tok+"""'"""
        the_file.write(content)
    import config

app = Client(config.TOKEN)

upp = '◻◻◻◻◻◻◻◻◻◻'
ctr = "◼"

manage = {}

#Function to download the file

def downloadFile(c,mid,msg):
    global manage
    try:
        data = msg.split(" | ")
        r = requests.get(data[0], allow_redirects=True,stream=True)
        print(r.headers)
        if(r.status_code < 400):
            if('text/html' not in r.headers['Content-Type'].lower()):
                if(int(r.headers['Content-Length'])/(1024*1024) < 1500):
                    if(len(data) > 1):
                        filename = data[1]
                    elif(r.headers.get('content-disposition') and "filename" in r.headers.get('content-disposition')):
                        filename = re.findall('filename=(.+)', r.headers.get('content-disposition'))[0].replace('"','')
                    elif(not r.url.split('/')[-1].split('#')[0].split('?')[0].isnumeric()):
                        filename = r.url.split('/')[-1].split('#')[0].split('?')[0].replace('%20','.')
                        try:
                            open(filename, 'wb')
                        except OSError:
                            filename = str(time.time())+str(mimetypes.guess_extension(r.headers['Content-Type']))
                    else:
                        filename = str(time.time())+str(mimetypes.guess_extension(r.headers['Content-Type']))
                        
                    s = time.time()
                    print(filename)
                    l = 0
                    with open(filename, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1024):
                            if(not manage['odysseusmax']):
                                break
                            l += len(chunk)
                            down(c,l,int(r.headers['Content-Length']),'odysseusmax',mid,'downloading')
                            fd.write(chunk)
                    print(int(r.headers['Content-Length'])/(1024*1024)/(time.time()-s))
                    if(manage['odysseusmax']):
                        return True,filename,int(r.headers['Content-Length'])/(1024*1024),(time.time()-s),r.headers['Content-Type'].lower()
                    else:
                        os.remove(filename)
                        return False,"**Download cancelled**"
                else:
                    return False,"**Size greater than 1.5 GB**"
            else:
                return False,"**Not a download link**"
        else:
            return False,"**Not a valid link**"
    except FileNotFoundError:
        return False,"**File Not Found**"
    except KeyError as e:
        if('content-length' in str(e)):
            return False,"**Length cannot be determined**"
    except Exception as e:
        print(str(e),type(e))
        return False,"**Unknown Error "+str(e)+"**"
  
def getLength(filename):
    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(filename))
    if metadata.has("duration"):
        duration = metadata.get('duration').seconds
    if metadata.has("width"):
        width = metadata.get("width")
    if metadata.has("height"):
        height = metadata.get("height")
    print(duration,width,height)
    return duration,width,height

down_progress = 0
def down(c, cur, tot, chat_id, message_id,status):
    global upp, down_progress,manage
    progress = cur * 100 // tot
    if(not manage['odysseusmax']):
        c.stop_transmission()

    if (progress != down_progress and progress % 10 == 0):
        pp = int(progress/10)
        try:
            c.edit_message_text(chat_id,message_id,"{}\n{} {}%`".format(status,upp.replace('◻','◼',pp),progress))
            down_progress = progress
        except Exception as e:
            print(e)
            pass
    else:
        return


@app.on_message(Filters.command(["cancel"]) & Filters.private)
def cancl(client, message):
    print(message)
    global manage
    if(manage['odysseusmax']):
        manage['odysseusmax'] = False
    else:
        client.send_message('odysseusmax',"not processing anything")


#Responce for messages
@app.on_message(Filters.text & Filters.private)
def mess(client, message):
    global manage
    if(message.entities and message.entities[0].type in 'url'):
        msg = client.send_message('odysseusmax',"trying to download")
        manage['odysseusmax'] = True
        dl = downloadFile(client,msg.message_id,message.text)
        if(dl[0]):
            client.delete_messages('odysseusmax',msg.message_id,True)
            msg = client.send_message('odysseusmax',"uploading")
            s=time.time()
            print(dl)
            if('video' in dl[4]):
                duration,width,height = getLength(dl[1])
                snt = client.send_video(chat_id='odysseusmax',video=dl[1],duration=duration,width=width,height=height,thumb='downloads/thumb.jpeg',supports_streaming=True,reply_to_message_id=message.message_id,progress=down,progress_args=('odysseusmax',msg.message_id,'uploading',))
            else:
                snt = client.send_document(chat_id='odysseusmax',document=dl[1],thumb='downloads/thumb.jpeg',reply_to_message_id=message.message_id,progress=down,progress_args=('odysseusmax',msg.message_id,'uploading',))
            e=time.time()-s
            client.delete_messages('odysseusmax',msg.message_id,True)
            client.edit_message_caption('odysseusmax',snt.message_id,"uploaded in {}\n\nspeed = {}".format(e,dl[2]/e))
            os.remove(dl[1])
            manage.pop('odysseusmax')
            
        else:
            client.delete_messages('odysseusmax',msg.message_id,True)
            client.send_message('odysseusmax',dl[1])

@app.on_message(Filters.document & Filters.private)
def video(client, message):
    global manage
    if('video' in message.document.mime_type):
        file_name = ''
        if(message.document.file_name):
            file_name = message.document.file_name
        msg = client.send_message(chat_id='odysseusmax',
                                text="downloading")
        manage['odysseusmax'] = True
        s = time.time()
        file = client.download_media(message=message,
                                    file_name=file_name,
                                    progress=down,
                                    progress_args=('odysseusmax',msg.message_id,'Downloading...',)
                                    )
        e = time.time()-s
        print((message.document.file_size/(1024*1024))/e)
        duration, width, height = getLength(file)
        
        s = time.time()
        snt = client.send_video(chat_id='odysseusmax',
                                video=file,
                                duration=duration,
                                width=width,
                                height=height,
                                thumb='downloads/thumb.jpeg',
                                supports_streaming=True,
                                reply_to_message_id=message.message_id,
                                progress=down,
                                progress_args=('odysseusmax',msg.message_id,'uploading to telegram',)
                                )
        e = time.time()-s
        client.delete_messages('odysseusmax',msg.message_id,True)
        client.edit_message_caption('odysseusmax',snt.message_id,"uploaded in {}\n\nspeed = {}".format(e,(message.document.file_size/(1024*1024))/e))



      
@app.on_message(Filters.photo & Filters.private)
def foto(client, message):
    print(message.photo)
    g = client.download_media(message=message.photo.sizes[0],file_name='thumb.jpeg')
    print(g)
    client.send_message('odysseusmax',"thumb saved succesfully")
       
app.run()
