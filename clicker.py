import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui
import threading
import time
import random
from datetime import datetime, timedelta
import platform

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # Ayarlar penceresi
        self.window = tk.Toplevel(parent)
        self.window.title('Ayarlar')
        self.window.geometry('280x280')
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Başlangıç saati
        start_frame = tk.Frame(self.window)
        start_frame.pack(pady=5)
        tk.Label(start_frame, text='Başlangıç:').pack(side=tk.LEFT)
        
        self.start_hour_var = tk.StringVar(value='09')
        self.start_hour_combo = ttk.Combobox(start_frame, textvariable=self.start_hour_var, width=2, values=[f'{i:02d}' for i in range(24)])
        self.start_hour_combo.pack(side=tk.LEFT, padx=1)
        tk.Label(start_frame, text=':').pack(side=tk.LEFT)
        
        self.start_minute_var = tk.StringVar(value='00')
        self.start_minute_combo = ttk.Combobox(start_frame, textvariable=self.start_minute_var, width=2, values=[f'{i:02d}' for i in range(60)])
        self.start_minute_combo.pack(side=tk.LEFT, padx=1)

        # Zaman modu seçimi
        mode_frame = tk.Frame(self.window)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text='Zaman Modu:').pack(anchor=tk.W)
        
        self.mode_var = tk.StringVar(value='hourly')
        
        # Saat + Dakika modu frame'i
        self.hourly_frame = tk.Frame(mode_frame)
        self.hourly_frame.pack(anchor=tk.W, padx=10, pady=2)
        self.hourly_radio = tk.Radiobutton(self.hourly_frame, text='Saat + Dakika (', variable=self.mode_var, value='hourly', command=self.toggle_mode)
        self.hourly_radio.pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(self.hourly_frame, width=3)
        self.interval_entry.insert(0, '2')
        self.interval_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(self.hourly_frame, text='saat +  dk)').pack(side=tk.LEFT)
        
        # Sadece Dakika modu
        self.minute_radio = tk.Radiobutton(mode_frame, text='Sadece Dakika (40-60 dk aralık)', variable=self.mode_var, value='minute', command=self.toggle_mode)
        self.minute_radio.pack(anchor=tk.W, padx=10, pady=2)

        # Tekrar sayısı
        repeat_frame = tk.Frame(self.window)
        repeat_frame.pack(pady=5)
        tk.Label(repeat_frame, text='Günlük Tekrar:').pack(side=tk.LEFT)
        self.repeat_entry = tk.Entry(repeat_frame, width=3)
        self.repeat_entry.insert(0, '6')
        self.repeat_entry.pack(side=tk.LEFT, padx=2)

        # Bekleme süresi aralığı
        wait_frame = tk.Frame(self.window)
        wait_frame.pack(pady=5)
        tk.Label(wait_frame, text='Min:').pack(side=tk.LEFT)
        self.min_wait_entry = tk.Entry(wait_frame, width=3)
        self.min_wait_entry.insert(0, '40')
        self.min_wait_entry.pack(side=tk.LEFT, padx=1)
        tk.Label(wait_frame, text='Max:').pack(side=tk.LEFT)
        self.max_wait_entry = tk.Entry(wait_frame, width=3)
        self.max_wait_entry.insert(0, '60')
        self.max_wait_entry.pack(side=tk.LEFT, padx=1)
        tk.Label(wait_frame, text='dk').pack(side=tk.LEFT)
        
        # Input değişikliklerini dinle
        self.min_wait_entry.bind('<KeyRelease>', self.update_wait_labels)
        self.max_wait_entry.bind('<KeyRelease>', self.update_wait_labels)
        
        # Başlangıç label'larını güncelle
        self.update_wait_labels()

        # Butonlar
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text='Tamam', command=self.ok_clicked, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='İptal', command=self.cancel_clicked, width=8).pack(side=tk.LEFT, padx=5)

        # Mod değişikliğini başlat
        self.toggle_mode()

        # Pencereyi ortala
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def toggle_mode(self):
        # Artık hourly_frame her zaman görünür, sadece input'u aktif/pasif yapıyoruz
        if self.mode_var.get() == 'hourly':
            self.interval_entry.config(state='normal')
        else:
            self.interval_entry.config(state='disabled')

    def update_wait_labels(self, event=None):
        """Min-max değerlerini label'larda günceller"""
        try:
            min_val = self.min_wait_entry.get()
            max_val = self.max_wait_entry.get()
            
            # Saat + Dakika modu label'ını güncelle
            if hasattr(self, 'hourly_frame'):
                for widget in self.hourly_frame.winfo_children():
                    if isinstance(widget, tk.Label) and 'saat +' in widget.cget('text'):
                        widget.config(text=f'saat + {min_val}-{max_val} dk)')
                        break
            
            # Sadece Dakika modu label'ını güncelle
            self.minute_radio.config(text=f'Sadece Dakika ({min_val}-{max_val} dk aralık)')
        except:
            pass

    def ok_clicked(self):
        try:
            self.result = {
                'start_hour': int(self.start_hour_var.get()),
                'start_minute': int(self.start_minute_var.get()),
                'mode': self.mode_var.get(),
                'interval_hours': int(self.interval_entry.get()) if self.mode_var.get() == 'hourly' else 0,
                'daily_repeat': int(self.repeat_entry.get()),
                'min_wait': float(self.min_wait_entry.get()),
                'max_wait': float(self.max_wait_entry.get())
            }
            self.window.destroy()
        except ValueError:
            messagebox.showerror('Hata', 'Geçerli değerler girin!')

    def cancel_clicked(self):
        self.window.destroy()

class LogWindow:
    def __init__(self, parent, logs):
        self.window = tk.Toplevel(parent)
        self.window.title('Log Geçmişi')
        self.window.geometry('400x300')
        self.window.transient(parent)
        
        # Log alanı
        log_frame = tk.Frame(self.window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, font=('Consolas', 9))
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Logları ekle
        for log in logs:
            self.log_text.insert(tk.END, log + '\n')
        
        self.log_text.see(tk.END)
        
        # Kapat butonu
        tk.Button(self.window, text='Kapat', command=self.window.destroy).pack(pady=5)
        
        # Pencereyi ortala
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

class ClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Clicker')
        self.root.geometry('250x100')
        
        # Pencereyi sürekli en üstte tut
        self.root.attributes('-topmost', True)
        
        # Windows'ta ek özellikler
        if platform.system() == 'Windows':
            try:
                # Windows API ile always on top
                import ctypes
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004)
            except:
                pass
        
        self.point = None
        self.running = False
        self.countdown_thread = None
        self.continuous_thread = None
        self.countdown_running = False
        self.logs = []
        
        # Güvenlik özellikleri
        self.click_count = 0
        self.last_click_time = None
        self.safety_check_thread = None

        # Varsayılan ayarlar
        self.default_settings = {
            'start_hour': 9,
            'start_minute': 0,
            'mode': 'hourly',
            'interval_hours': 2,
            'daily_repeat': 6,
            'min_wait': 40,
            'max_wait': 60
        }
        
        # Mevcut ayarlar (varsayılan ile başla)
        self.settings = self.default_settings.copy()

        # Üst butonlar
        top_frame = tk.Frame(root)
        top_frame.pack(pady=2)
        
        self.select_btn = tk.Button(top_frame, text='Nokta', command=self.select_point, width=5, font=('Arial', 8))
        self.select_btn.pack(side=tk.LEFT, padx=1)
        
        self.settings_btn = tk.Button(top_frame, text='Ayarlar', command=self.open_settings, width=5, font=('Arial', 8))
        self.settings_btn.pack(side=tk.LEFT, padx=1)
        
        self.log_btn = tk.Button(top_frame, text='Log', command=self.show_logs, width=5, font=('Arial', 8))
        self.log_btn.pack(side=tk.LEFT, padx=1)

        # Durum
        self.status = tk.Label(root, text='Hazır', font=('Arial', 8), fg='blue')
        self.status.pack(pady=1)

        # Sayaç
        self.countdown = tk.Label(root, text='', font=('Arial', 9, 'bold'), fg='red')
        self.countdown.pack(pady=1)

        # Alt butonlar
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=2)
        
        self.start_btn = tk.Button(bottom_frame, text='Başlat', command=self.start_continuous_clicking, width=5, font=('Arial', 8))
        self.start_btn.pack(side=tk.LEFT, padx=1)
        
        self.stop_btn = tk.Button(bottom_frame, text='Durdur', command=self.stop_clicking, state=tk.DISABLED, width=5, font=('Arial', 8))
        self.stop_btn.pack(side=tk.LEFT, padx=1)

        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Acil durum kapatma tuşu (Alt+E)
        self.root.bind('<Alt-e>', self.emergency_shutdown)
        self.root.bind('<Alt-E>', self.emergency_shutdown)
        
        # Başlangıç başlığını ayarla
        self.update_window_title()

    def update_window_title(self):
        if self.settings['mode'] == 'hourly':
            mode_text = f"Saat + Dakika ({self.settings['interval_hours']} saat)"
        else:
            mode_text = "Sadece Dakika"
        self.root.title(f'{mode_text} Modu')

    def emergency_shutdown(self, event=None):
        """Acil durum kapatma - Alt+E ile programı kapatır"""
        self.log_message("Acil durum kapatma tetiklendi (Alt+E)")
        if self.running:
            self.stop_clicking()
        self.root.destroy()

    def safety_shutdown(self, reason):
        """Güvenlik nedeniyle otomatik kapatma"""
        self.log_message(f"GÜVENLİK UYARISI: {reason} - Program otomatik kapatılıyor!")
        if self.running:
            self.stop_clicking()
        self.root.destroy()

    def check_safety_limits(self):
        """Güvenlik limitlerini kontrol eder - 1 dakika içinde 100 tıklama"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Son 1 dakika içindeki tıklamaları say
                if self.last_click_time:
                    time_diff = (current_time - self.last_click_time).total_seconds()
                    if time_diff > 60:  # 1 dakika geçtiyse sayacı sıfırla
                        self.click_count = 0
                        self.last_click_time = None
                
                # 1 dakika içinde 100'den fazla tıklama varsa kapat
                if self.click_count >= 100:
                    self.root.after(0, lambda: self.safety_shutdown("1 dakika içinde 100 tıklama limiti aşıldı"))
                    break
                
                time.sleep(1)  # Her saniye kontrol et
                
            except Exception as e:
                self.log_message(f"Güvenlik kontrolü hatası: {str(e)}")
                time.sleep(1)

    def show_logs(self):
        if self.logs:
            LogWindow(self.root, self.logs)
        else:
            messagebox.showinfo('Log', 'Henüz log bulunmuyor.')

    def open_settings(self):
        settings_window = SettingsWindow(self.root)
        self.root.wait_window(settings_window.window)
        
        if settings_window.result:
            self.settings = settings_window.result
            mode_text = "Saat + Dakika" if self.settings['mode'] == 'hourly' else "Sadece Dakika"
            self.log_message(f"Ayarlar güncellendi: {self.settings['start_hour']:02d}:{self.settings['start_minute']:02d}, {mode_text}, {self.settings['daily_repeat']} tekrar")
            self.update_window_title()

    def on_closing(self):
        if self.running:
            if messagebox.askokcancel("Çıkış", "Program çalışıyor. Gerçekten çıkmak istiyor musunuz?"):
                self.stop_clicking()
                self.root.destroy()
        else:
            self.root.destroy()

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
        
        # Son 100 logu tut
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

    def select_point(self):
        messagebox.showinfo('Nokta Seç', 'Tıklanacak noktayı seçmek için 3 saniye içinde mouse ile istediğiniz yere gelin.')
        self.root.withdraw()
        time.sleep(3)
        x, y = pyautogui.position()
        self.point = (x, y)
        self.root.deiconify()
        messagebox.showinfo('Nokta Seçildi', f'Seçilen Nokta: X={x}, Y={y}')
        self.log_message(f"Nokta: X={x}, Y={y}")

    def start_countdown(self, total_seconds):
        # Önceki sayaç thread'ini durdur
        self.countdown_running = False
        if self.countdown_thread and self.countdown_thread.is_alive():
            time.sleep(0.1)  # Kısa bir bekleme
        
        # Yeni sayaç thread'ini başlat
        self.countdown_running = True
        self.countdown_thread = threading.Thread(target=self.countdown_timer, args=(total_seconds,), daemon=True)
        self.countdown_thread.start()

    def start_continuous_clicking(self):
        if not self.point:
            messagebox.showwarning('Uyarı', 'Önce tıklanacak noktayı seçin!')
            return
        
        try:
            # Ayarları kopyala (thread güvenliği için)
            current_settings = self.settings.copy()
            
            start_hour = current_settings['start_hour']
            start_minute = current_settings['start_minute']
            mode = current_settings['mode']
            interval_hours = current_settings['interval_hours']
            daily_repeat = current_settings['daily_repeat']
            min_wait = current_settings['min_wait']
            max_wait = current_settings['max_wait']
            
            if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
                raise ValueError("Geçersiz saat")
            if mode == 'hourly' and interval_hours <= 0:
                raise ValueError("Saat aralığı 0'dan büyük olmalı")
            if min_wait > max_wait:
                min_wait, max_wait = max_wait, min_wait
        except ValueError as e:
            messagebox.showerror('Hata', f'Geçerli değerler girin! {str(e)}')
            return
        
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        if mode == 'hourly':
            mode_text = f"Saat + Dakika ({interval_hours} saat)"
        else:
            mode_text = "Sadece Dakika"
        self.status.config(text='Başlatıldı', fg='green')
        self.log_message(f"Başlatıldı - {start_hour:02d}:{start_minute:02d}, {mode_text}, {daily_repeat} tekrar")
        
        # Güvenlik kontrol thread'ini başlat
        self.safety_check_thread = threading.Thread(target=self.check_safety_limits, daemon=True)
        self.safety_check_thread.start()
        
        # Sürekli çalışma thread'ini başlat
        self.continuous_thread = threading.Thread(
            target=self.continuous_click_loop, 
            args=(start_hour, start_minute, mode, interval_hours, daily_repeat, min_wait, max_wait), 
            daemon=True
        )
        self.continuous_thread.start()

    def continuous_click_loop(self, start_hour, start_minute, mode, interval_hours, daily_repeat, min_wait, max_wait):
        try:
            if mode == 'hourly':
                # Saat + Dakika modu: Başlangıç saati bekle
                now = datetime.now()
                today_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                
                # Eğer başlangıç saati bugün geçtiyse, yarına ayarla
                if today_start <= now:
                    today_start += timedelta(days=1)
                
                # İlk başlangıca kadar bekle
                time_to_start = (today_start - now).total_seconds()
                if time_to_start > 0:
                    self.status.config(text=f'Bekleniyor: {today_start.strftime("%H:%M")}', fg='orange')
                    self.log_message(f"Bekleniyor: {today_start.strftime('%H:%M')}")
                    
                    # Başlangıç sayacı
                    self.start_countdown(time_to_start)
                    time.sleep(time_to_start)
            else:
                # Sadece Dakika modu: İlk bekleme süresi
                random_minutes = random.uniform(min_wait, max_wait)
                total_wait_seconds = random_minutes * 60
                
                next_click_time = datetime.now() + timedelta(seconds=total_wait_seconds)
                self.status.config(text=f'İlk bekleme: {next_click_time.strftime("%H:%M")} ({random_minutes:.1f} dk)', fg='orange')
                self.log_message(f"Sadece dakika modu - ilk bekleme: {random_minutes:.1f} dk")
                
                # İlk bekleme sayacı
                self.start_countdown(total_wait_seconds)
                time.sleep(total_wait_seconds)
            
            if not self.running:
                return
            
            # Günlük tıklama döngüsü
            if mode == 'hourly':
                mode_text = f"Saat + Dakika ({interval_hours} saat)"
            else:
                mode_text = "Sadece Dakika"
            self.log_message(f"Döngü başladı - {daily_repeat} tekrar, {mode_text}")
            
            for i in range(daily_repeat):
                if not self.running:
                    break
                
                # Tıklama yap
                click_time = datetime.now().strftime("%H:%M:%S")
                pyautogui.click(self.point)
                
                # Güvenlik sayacını güncelle
                self.click_count += 1
                self.last_click_time = datetime.now()
                
                self.log_message(f"Tıklandı: {click_time} ({i+1}/{daily_repeat})")
                self.status.config(text=f'Tıklandı: {click_time} ({i+1}/{daily_repeat})', fg='red')
                
                # Son tıklama değilse bekle
                if i < daily_repeat - 1 and self.running:
                    if mode == 'hourly':
                        # Saat aralığı + random dakika süresi
                        interval_seconds = interval_hours * 3600  # Saat aralığı
                        random_minutes = random.uniform(min_wait, max_wait)
                        random_seconds = random_minutes * 60
                        total_wait_seconds = interval_seconds + random_seconds
                        
                        next_click_time = datetime.now() + timedelta(seconds=total_wait_seconds)
                        self.status.config(text=f'Sonraki: {next_click_time.strftime("%H:%M")} ({random_minutes:.1f} dk) ({i+1}/{daily_repeat})', fg='blue')
                        self.log_message(f"Sonraki: {next_click_time.strftime('%H:%M')} ({random_minutes:.1f} dk bekleme)")
                    else:
                        # Sadece random dakika süresi
                        random_minutes = random.uniform(min_wait, max_wait)
                        total_wait_seconds = random_minutes * 60
                        
                        next_click_time = datetime.now() + timedelta(seconds=total_wait_seconds)
                        self.status.config(text=f'Sonraki: {next_click_time.strftime("%H:%M")} ({random_minutes:.1f} dk) ({i+1}/{daily_repeat})', fg='blue')
                        self.log_message(f"Sonraki: {next_click_time.strftime('%H:%M')} ({random_minutes:.1f} dk bekleme)")
                    
                    # Bekleme sayacı
                    self.start_countdown(total_wait_seconds)
                    time.sleep(total_wait_seconds)
            
            if self.running:
                self.log_message("Döngü tamamlandı - Otomatik durduruluyor")
                self.status.config(text='Döngü tamamlandı', fg='green')
                # Döngü tamamlandığında otomatik durdur
                self.root.after(0, self.stop_clicking)
            
        except Exception as e:
            self.log_message(f"Hata: {str(e)}")
            if self.running:
                self.root.after(0, self.stop_clicking)

    def countdown_timer(self, total_seconds):
        remaining = total_seconds
        while remaining > 0 and self.running and self.countdown_running:
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            seconds = int(remaining % 60)
            
            if hours > 0:
                self.countdown.config(text=f'Kalan: {hours:02d}:{minutes:02d}:{seconds:02d}')
            else:
                self.countdown.config(text=f'Kalan: {minutes:02d}:{seconds:02d}')
            
            time.sleep(1)
            remaining -= 1
        
        if self.running and self.countdown_running:
            self.countdown.config(text='Tıklama yapılıyor...')

    def stop_clicking(self):
        self.running = False
        self.countdown_running = False
        self.status.config(text='Durduruldu', fg='red')
        self.countdown.config(text='')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Güvenlik sayaçlarını sıfırla
        self.click_count = 0
        self.last_click_time = None
        
        # Ayarları varsayılan değerlere sıfırla
        self.settings = self.default_settings.copy()
        
        # Logları temizle
        self.logs.clear()
        
        self.log_message("Durduruldu - Ayarlar ve loglar sıfırlandı")

if __name__ == '__main__':
    root = tk.Tk()
    app = ClickerApp(root)
    root.mainloop() 