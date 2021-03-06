from serial_thread import *;
import time,json ;
import Queue,thread,threading ;
from constant_len_list import * ;
from Crypto.Cipher import AES

class serial_manager(threading.Thread):
    
    def __init__(self,port='/dev/ttyUSB0',rate=115200,cache_size=240):
        threading.Thread.__init__(self);
        self.cache_size = cache_size ;
        self.sth = serial_listen_thread(port,rate);
        self.cache = {};
        self.cache_list = {} ;
        self.cmd_queue = Queue.Queue();
        self.running = False ;
        self.key = '1234567890abcdef'
        self._d  = AES.new(self.key, AES.MODE_ECB, b'0' * 16);
       
    def set_serial_port(self,port,rate):
        return self.sth.set_serial_port(port,rate);

    def set_cache_size(self,cache_size):
        self.cache_size = cache_size ;

    
    def run(self):
        try:
            self.sth.start();
            thread.start_new_thread(self.__refresh_cache__,());
            thread.start_new_thread(self.__refresh_list__,());
            self.running = True ;
        except :
            self.running = False ;
    
    def stop(self):
        self.running = False ;
        
    def __refresh_cache__(self):
        while self.running == True :
            try:
                rtn = self.sth.recv_queue.get();
                res = self._d.decrypt(a2b_hex(rtn[:320])).decode('utf-8')
                res = res[:res.rfind('}') + 1]
                #print res ;
                var_table = json.loads(res);
                for var in var_table :
                    self.cache[var] = var_table[var] ;
            except Exception as e:
                print str(e);
            time.sleep(0.01)         
    
    def get_var(self,key):
        if self.running ==  False :
            raise Exception("Serial port manger is not running");
        return self.cache[key];

    def get_var_table(self):
        if self.running ==  False :
            raise Exception("Serial port manger is not running");
        return self.cache ;

    def send_command(self,cmd):
        if self.running ==  False :
            raise Exception("Serial port manger is not running");
        return self.sth.send(cmd);
            
    def __refresh_list__(self):
        start_time = time.time();
        cnt = 0 ;
        while self.running == True :
            time.sleep(0.1);
            if time.time() > start_time + cnt :
                cnt = cnt + 1 ;
                for key in self.cache :
                    if not self.cache_list.has_key(key) :
                        self.cache_list[key] = constant_len_list(self.cache_size);
                    else :
                        self.cache_list[key].num = self.cache_size ;
                    self.cache_list[key].add_tail(self.get_var(key));
    
    def get_var_list(self,key):
        if self.running ==  False :
            raise Exception("Serial port manger is not running");
        l = self.cache_list[key].get_data();
        return l ;


if __name__ == '__main__':
    print "test begin."                    
    sm = serial_manager();
    sm.start();
    for i in range(100):
        time.sleep(2);
        print sm.get_var_table();
        #for key in sm.cache_list :
        #    print str(key),str(sm.cache_list[key])
        #print i