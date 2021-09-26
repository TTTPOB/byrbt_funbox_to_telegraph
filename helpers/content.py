from bs4 import BeautifulSoup as bs
import re
from pathlib import Path
from telegraph import Telegraph
from telegraph.upload import upload_file
from PIL import Image

def content_to_telegraph(content, title,timeNow, httpx_client, config):
  # contentChildren=list(list(content.children)[0].children)
  contentChildren=list(content.children)
  
  imageFileDir="img/"+timeNow
  Path(imageFileDir).mkdir(parents=True,exist_ok=True)
  telegraph=Telegraph(config["telegraph"]["access_token"])
  
  def processingImgTag(tag):
    imageUrl=tag["src"]
    if re.match(".*(jpg|jpeg|png|gif).thumb.jpg$", imageUrl):
      imageUrl = re.sub(".thumb.jpg$", "", imageUrl)
    elif re.match(".*(jpg|jpeg|png|gif).jpg$", imageUrl):
      imageUrl = re.sub(".jpg$", "", imageUrl)
    else:
      imageUrl = re.sub("thumb.(?=jpg$)", "", imageUrl)
  
    fileName = imageUrl[imageUrl.rindex("/")+1:]
    filePath=Path(imageFileDir+"/"+fileName)
    print(filePath)
    if not filePath.is_file():
      resp=httpx_client.get(imageUrl)
      if resp.status_code == 200:
        print("resp ok")
        with open(filePath,"wb") as img:
          img.write(resp.content)
      else:
        return bs("<img src={}/>".format("https://via.placeholder.com/350x150"), "html.parser").img
  
    if filePath.stat().st_size > 5e6:
      return bs("<p>这图太大了telegraph不让传(限制5m)，改天找了图床再说</p>", "html.parser").p
      webpPath = str(filePath)+".webp"
      origImg = Image.open(filePath).convert("RGB")
      origImg.save(webpPath, "webp")
      filePath = str(webpPath)
  
    # if (getattr(Image.open(filePath), "is_animated", False)):
      # videoPath=f"{str(filePath)}.mp4"
      # print("converting animated image to mp4 video")
      # (
        # ffmpeg
          # .input(str(filePath))
          # .output(videoPath)
          # .run()
      # )
      # print(videoPath)
      # filePath = str(videoPath)
      # newLink=upload_file(filePath)[0]
      # return bs("<video src={} />".format(newLink), "html.parser").video
  
  
    filePath = str(filePath)
    newLink=upload_file(filePath)[0]
    return bs("<img src={} />".format(newLink),"html.parser").img
  
  def processingTextTag(tag):
    if tag.name in ["b","i","u","p"]:
      return(tag)
    elif tag.name in ["font","span"]:
      tagText=tag.text.strip("\r\n")
      if tagText != "":
        return bs("<p>{}</p>".format(tagText), "html.parser").p
      else:
        return(None)
    elif tag.name in [None]:
      tagText=str(tag).strip("\r\n")
      if tagText != "":
        return bs("<p>{}</p>".format(tagText), "html.parser").p
      else:
        return(None)
  
  def processingTag(tag):
    if tag.name == "img":
      return(processingImgTag(tag))
    elif tag.name in ["b","i","u","p","font","span",None]:
      print(tag)
      return(processingTextTag(tag))
    else:
      return None
  
  processedTagList=[processingTag(tag) for tag in contentChildren]
  processedTagList=[tag for tag in processedTagList if tag != None]
  
  telegraphReturn = telegraph.create_page(
    title="今日趣味盒--"+title,
    author_name="byrbtFunBox",
    author_url="https://t.me/byrbtFunBox",
    html_content="\n".join([str(tag) for tag in processedTagList])
  )
  return(telegraphReturn)
  
  