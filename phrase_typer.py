import json
import keyboard
import time
import sys
import threading
class PhraseTyper :
    def __init__ (self ,json_file ="phrases.json"):
        self .json_file =json_file
        self .phrases =[]
        self .current_index =0
        self .running =False
        self .last_press_time =0
        self .debounce_delay =0.8
        self .lock =threading .Lock ()
    def load_phrases (self ):
        try :
            with open (self .json_file ,'r',encoding ='utf-8')as f :
                self .phrases =json .load (f ).get ('phrases',[])
                print (f"Загружено {len (self .phrases )} фраз")
                return True
        except :
            print (f"Файл {self .json_file } не найден")
            return False
    def save_phrases (self ,text ):
        lines =[line .strip ()for line in text .strip ().split ('\n')if line .strip ()]
        with open (self .json_file ,'w',encoding ='utf-8')as f :
            json .dump ({'phrases':lines },f ,ensure_ascii =False ,indent =2 )
        self .phrases ,self .current_index =lines ,0
        print (f"Сохранено {len (lines )} фраз")
    def type_next_phrase (self ):
        if not self .lock .acquire (blocking =False )or not self .phrases :
            return
        try :
            if time .time ()-self .last_press_time <self .debounce_delay :
                return
            self .last_press_time =time .time ()
            if self .current_index >=len (self .phrases ):
                self .current_index =0
            time .sleep (0.3 )
            keyboard .write (self .phrases [self .current_index ])
            print (f"Введена {self .current_index +1 }/{len (self .phrases )}: {self .phrases [self .current_index ]}")
            self .current_index +=1
        finally :
            self .lock .release ()
    def stop (self ):
        self .running =False
        print ("\nОстановлено")
        keyboard .unhook_all ()
        sys .exit (0 )
    def start_listening (self ):
        if not self .phrases :
            print ("Нет фраз для ввода!")
            return
        self .running =True
        print ("\nПрограмма запущена! END - ввод фразы, ESC - выход\n")
        keyboard .add_hotkey ('end',lambda :self .type_next_phrase ()if self .running else None ,suppress =True )
        keyboard .add_hotkey ('esc',self .stop )
        keyboard .wait ('esc')
def main ():
    typer =PhraseTyper ()
    print ("1. Создать/обновить файл\n2. Запустить программу")
    choice =input ("Выбор: ").strip ()
    if choice =="1":
        print ("\nВставьте фразы (каждая строка - отдельная фраза). Двойной Enter или 'END' для завершения:")
        lines =[]
        while True :
            line =input ()
            if line =="END"or (line ==""and lines and lines [-1 ]!=""):
                break
            lines .append (line )
        typer .save_phrases ("\n".join ([l for l in lines if l .strip ()]))
    elif choice =="2":
        if typer .load_phrases ():
            typer .start_listening ()
if __name__ =="__main__":
    try :
        main ()
    except KeyboardInterrupt :
        print ("\nПрервано")
        sys .exit (0 )