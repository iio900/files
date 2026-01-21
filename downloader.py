# downloader.py
import aiohttp, re, urllib.parse, asyncio
from fake_useragent import UserAgent

API_BASE = "httpas://fly-wispy-wildflower-2967.fly.dev"

async def get_download_url(url: str):
    """جلب ستوريات انستغرام"""
    try:
        async with aiohttp.ClientSession() as session:
            # تأكد أن الـ username يبدأ بـ @
            if not url.startswith("@"):
                url = f"@{url}"
            
            # لا تستخدم encoding للـ @
            api_url = f"{API_BASE}/highlights/stories?username={url}"
            
            print(f"🔗 API Request: {api_url}")
            
            async with session.get(api_url, timeout=30) as response:
                print(f"📡 Response Status: {response.status}")
                
                # قراءة الرد النصي أولاً للديباگ
                text_response = await response.text()
                print(f"📄 Raw Response: {text_response[:500]}")
                
                if response.status != 200:
                    return []
                
                # محاولة تحويل إلى JSON
                try:
                    data = await response.json()
                    print(f"✅ JSON parsed, media_urls count: {len(data.get('media_urls', []))}")
                    return data.get("media_urls", [])
                except Exception as json_error:
                    print(f"❌ JSON parse error: {json_error}")
                    return []
    except Exception as e:
        print(f"🔥 Error: {e}")
        return []

async def get_highlights_list(username: str):
    try:
        async with aiohttp.ClientSession() as session:
            # تأكد من الـ username
            print(f"👤 Username received: '{username}'")
            
            api_url = f"{API_BASE}/highlights/highlights_list?username=@{username}"
            print(f"🔗 API URL: {api_url}")
            
            async with session.get(api_url, timeout=50) as response:
                print(f"📡 Response Status: {response.status}")
                
                if response.status != 200:
                    print(f"❌ HTTP Error: {response.status}")
                    return []
                
                # قراءة النص أولاً للديباگ
                text_response = await response.text()
                print(f"📄 Response length: {len(text_response)} chars")
                
                # محاولة تحويل إلى JSON
                try:
                    data = await response.json()
                    print(f"✅ JSON parsed successfully, found {len(data.get('highlights', []))} highlights")
                    highlights = data.get("highlights", [])
                    
                    result = []
                    for highlight in highlights:
                        result.append((highlight["id"], highlight["title"]))
                    return result
                    
                except Exception as json_error:
                    print(f"❌ JSON parse error: {json_error}")
                    print(f"📄 Raw response start: {text_response[:200]}")
                    return []
    except Exception as e:
        print(f"🔥 Exception in get_highlights_list: {type(e).__name__}: {e}")
        return []
async def get_highlight_media(highlight_id: str):
    """جلب روابط هايلايت محدد"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/highlights/highlight_media?highlight_id={highlight_id}"
            async with session.get(api_url, timeout=30) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return data.get("media_urls", [])
    except:
        return []
async def get_download_url_with_timeout(url: str, timeout: int):
    try:
        return await asyncio.wait_for(get_download_url(url), timeout=timeout)
    except:
        return None
        
        
        
        
# downloader.py - أضف في النهاية
async def youtube_search(query: str):
    """بحث في يوتيوب"""
    try:
        import json, re, time
        from urllib.parse import quote
        
        COOKIES = {
            "VISITOR_INFO1_LIVE": "YATQpNeOy0Y",
            "VISITOR_PRIVACY_METADATA": "CgJFRxIEGgAgVg%3D%3D", 
            "PREF": "f4=4000000&f6=40000000&tz=Africa.Cairo&f7=100&hl=ar&f5=30000",
            "YSC": "8cOXet1j-2o"
        }
        
        def extract_yt_initial_data(html):
            match = re.search(r'var ytInitialData\s*=\s*({.+?});</script>', html, re.DOTALL)
            if not match:
                match = re.search(r'window\["ytInitialData"\]\s*=\s*({.+?});</script>', html, re.DOTALL)
            if not match:
                match = re.search(r'ytInitialData\s*=\s*({.+?});</script>', html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            return None
        
        def find_video(data):
            if isinstance(data, dict):
                if "videoRenderer" in data:
                    return data["videoRenderer"]
                for key in ["contents", "secondaryContents", "primaryContents", "itemSectionContents"]:
                    if key in data:
                        result = find_video(data[key])
                        if result:
                            return result
                for v in data.values():
                    if isinstance(v, (dict, list)):
                        result = find_video(v)
                        if result:
                            return result
            elif isinstance(data, list):
                for item in data[:20]:
                    result = find_video(item)
                    if result:
                        return result
            return None
        
        def parse_video(vr):
            if not vr:
                return None
            url = vr.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", "")
            if not url.startswith("/watch"):
                return None
            is_live = vr.get("lengthText") is None
            if is_live:
                return {"error": "البث المباشر غير مدعوم"}
            title = vr.get("title", {}).get("runs", [{}])[0].get("text", "N/A")
            duration = vr.get("lengthText", {}).get("simpleText")
            views = vr.get("viewCountText", {}).get("simpleText", "").replace("مشاهدة", "").replace("مشاهدات", "").strip()
            channel = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "N/A")
            video_id_full = url.replace("/watch?v=", "")
            video_id = video_id_full.split("&")[0]
            return {
                "title": title,
                "duration": duration,
                "views": views,
                "channel": channel,
                "is_live": False,
                "id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
        
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        
        url = f"https://www.youtube.com/results?search_query={quote(query)}&hl=ar"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies=COOKIES, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    return {"error": "فشل في البحث"}
                html = await resp.text()
                data = extract_yt_initial_data(html)
                vr = find_video(data)
                result = parse_video(vr)
                if result:
                    return result
                else:
                    return {"error": "لم يتم العثور على الفيديو"}
    
    except Exception as e:
        return {"error": f"خطأ: {str(e)}"}
        



# في downloader.py نضيف دالة تويتر

async def get_twitter_media(url: str):
    """جلب معلومات تويتر"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/twitter/direct_link?url={url}"
            async with session.get(api_url) as response:
                return await response.json()
    except:
        return {"error": "فشل الاتصال"}


async def get_reddit_media(url: str):
    """جلب معلومات reddit"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/reddit/direct_link?url={url}"
            async with session.get(api_url, timeout=10) as response:
                return await response.json()
    except asyncio.TimeoutError:
        return {"error": "انتهت مهلة الاتصال"}
    except Exception:
        return {"error": "فشل الاتصال"}


async def get_pinterest_media(url: str):
    """جلب معلومات بنترست"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/pinterest/direct_link?url={url}"
            async with session.get(api_url, timeout=10) as response:
                return await response.json()
    except asyncio.TimeoutError:
        return {"error": "انتهت مهلة الاتصال"}
    except Exception:
        return {"error": "فشل الاتصال"}

async def get_tiktok_media(url: str):
    """جلب معلومات تيك توك"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/tiktok/direct_link?url={url}"
            async with session.get(api_url, timeout=10) as response:
                return await response.json()
    except asyncio.TimeoutError:
        return {"error": "انتهت مهلة الاتصال"}
    except Exception:
        return {"error": "فشل الاتصال"}

async def get_tiktok_audio(url: str):
    """جلب صوت تيك توك"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/tiktok/direct_audio?url={url}"
            async with session.get(api_url, timeout=10) as response:
                return await response.json()
    except asyncio.TimeoutError:
        return {"error": "انتهت مهلة الاتصال"}
    except Exception:
        return {"error": "فشل الاتصال"}


async def get_instagram_media_info(url: str):
    """جلب معلومات ملف انستغرام"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/instagram/direct_link?url={url}"
            async with session.get(api_url) as response:
                return await response.json()
    except:
        return {"error": "فشل الاتصال"}

async def get_instagram_audio(url: str):
    """جلب رابط صوت انستغرام"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/instagram/direct_audio?url={url}"
            async with session.get(api_url) as response:
                return await response.json()
    except:
        return {"error": "فشل الاتصال"}

async def get_facebook_media(url: str, max_retries: int = 2):
    """جلب معلومات فيسبوك مع مهلة 3 ثواني ومحاولة ثانية"""
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"{API_BASE}/facebook/direct_link?url={url}"
                
                # استخدم wait_for لتعيين مهلة 3 ثواني
                async with session.get(api_url) as response:
                    # مهلة 3 ثواني لكل محاولة
                    result = await asyncio.wait_for(response.json(), timeout=3)
                    return result
                    
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                print(f"انتهت المهلة، المحاولة {attempt + 2} من {max_retries}")
                continue  # حاول مرة أخرى
            else:
                return {"error": "انتهت مهلة الاتصال بعد عدة محاولات"}
        except aiohttp.ClientError as e:
            return {"error": f"فشل الاتصال: {str(e)}"}
        except Exception as e:
            return {"error": f"حدث خطأ: {str(e)}"}
    
    return {"error": "فشل بعد عدة محاولات"}

async def get_snapchat_media(url: str):
    """جلب معلومات سناب شات"""
    try:
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}/snapchat/direct_link?url={url}"
            async with session.get(api_url) as response:
                return await response.json()
    except:
        return {"error": "فشل الاتصال"}
