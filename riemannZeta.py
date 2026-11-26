# -*- coding: utf-8 -*-
"""
================================================================================
PROJE ADI: Riemann Zeta - Hipotez Test İstasyonu
YAZAR: Koray ve DeepSeek
TARİH: 2026

AÇIKLAMA:
Bu uygulama, Riemann Zeta fonksiyonunun kritik doğru (Re=0.5) üzerindeki 
sıfırlarını yüksek hassasiyetle tespit ederken; arka planda farklı gerçek 
kısım (Re) değerini de (0.3, 0.4, 0.6 vb.) test ederek Riemann Hipotezi'ni 
çürütme (falsification) potansiyelini arar. 

Kullanılan Teknolojiler: Python, Tkinter (Arayüz), Mpmath (Yüksek Hassasiyet), 
Matplotlib (Görselleştirme).
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mpmath as mp
import threading
import time
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# ==============================================================================
# KONFİGÜRASYON SABİTLERİ
# ==============================================================================
mp.mp.dps = 20  # Virgülden sonra 20 basamak hassasiyet (Yüksek hassasiyetli hesap)
HATA_ESIGI = mp.mpf('1e-10') # Sıfır kabul etmek için gereken maksimum hata payı

class ZetaHunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Riemann Zeta - Sıfır Avcısı ve Hipotez Test İstasyonu")
        self.root.geometry("1200x850")
        self.root.configure(bg="#2b2b2b")
        
        # --- Durum Değişkenleri ---
        self.is_running = False
        self.current_t = 25000.0
        self.found_zeros = []
        self.last_found_t = 0.0
        self.auto_scale = True 
        
        # --- Hipotez Çürütme (Falsification) Parametreleri ---
        # Kritik doğru (0.5) dışındaki, sıfır ihtimali barındıran test bölgeleri
        self.test_re_values = [0.3, 0.4, 0.45, 0.55, 0.6, 0.7] 
        self.test_re_index = 0
        self.test_t = 1.0 
        
        self.setup_ui()

    def setup_ui(self):
        """Kullanıcı arayüzünü (UI) oluşturan ana fonksiyon."""
        
        # --- ÜST PANEL (Kontrol Butonları ve Bilgi) ---
        top_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10, padx=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.btn_start = tk.Button(top_frame, text="▶ TARAMAYI BAŞLAT", bg="#28a745", fg="white", font=("Arial", 12, "bold"), command=self.start_scan)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        self.btn_stop = tk.Button(top_frame, text="⏹ DURDUR", bg="#dc3545", fg="white", font=("Arial", 12, "bold"), state=tk.DISABLED, command=self.stop_scan)
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        self.lbl_status = tk.Label(top_frame, text="Durum: Bekliyor", fg="#f1c40f", bg="#2b2b2b", font=("Arial", 12, "bold"))
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        
        self.lbl_t = tk.Label(top_frame, text=f"Kritik T: {self.current_t:.2f} | Test Re: 0.3", fg="white", bg="#2b2b2b", font=("Consolas", 11))
        self.lbl_t.pack(side=tk.RIGHT, padx=20)

        # --- ORTA PANEL (Log ve Sonuç Tablosu) ---
        middle_frame = tk.Frame(self.root, bg="#2b2b2b")
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Sol: İşlem Günlüğü
        left_frame = tk.Frame(middle_frame, bg="#2b2b2b", width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="İşlem Günlüğü:", fg="white", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_box = tk.Text(left_frame, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10), state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        # Log kutusuna kırmızı alarm metni için özel renk tanımı
        self.log_box.tag_config("alarm", foreground="red", font=("Consolas", 12, "bold"))

        # Sağ: Bulunan Sıfırlar Tablosu
        right_frame = tk.Frame(middle_frame, bg="#2b2b2b")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Bulunan Kesin Sıfırlar (Kritik Doğru):", fg="white", bg="#2b2b2b", font=("Arial", 10, "bold")).pack(anchor="w")
        
        cols = ("#", "t Değeri (Kesin)", "Hata Payı")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        self.tree.heading("#", text="#")
        self.tree.heading("t Değeri (Kesin)", text="t Değeri")
        self.tree.heading("Hata Payı", text="Hata Payı")
        self.tree.column("#", width=50, anchor="center")
        self.tree.column("t Değeri (Kesin)", width=250)
        self.tree.column("Hata Payı", width=150, anchor="center")
        
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # --- ALT PANEL (Grafikler) ---
        bottom_frame = tk.Frame(self.root, bg="#2b2b2b")
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.fig = Figure(figsize=(10, 4), dpi=100, facecolor="#2b2b2b")
        
        # Grafik 1: Kritik Doğru Üzerindeki Sıfırlar
        self.ax1 = self.fig.add_subplot(121)
        self.ax1.set_facecolor("#1e1e1e")
        self.ax1.set_title("Kritik Doğru (Re=0.5)", color="white")
        self.ax1.tick_params(colors="white")
        self.ax1.set_xlim(0.4, 0.6)
        self.ax1.set_ylim(24950, 25050)
        self.scatter, = self.ax1.plot([], [], 'ro', markersize=6)
        self.ax1.axvline(x=0.5, color="blue", linestyle="--")
        self.ax1.grid(True, color="#333333")
        
        # Grafik 2: Sıfır Yoğunluğu
        self.ax2 = self.fig.add_subplot(122)
        self.ax2.set_facecolor("#1e1e1e")
        self.ax2.set_title("Sıfır Yoğunluğu (N)", color="white")
        self.ax2.tick_params(colors="white")
        self.line_density, = self.ax2.plot([], [], 'g-', linewidth=2)
        self.ax2.grid(True, color="#333333")
        
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=bottom_frame)
        self.canvas.draw()
        
        # Fare tıklama olaylarını bağla
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Matplotlib Araç Çubuğu (Zoom, Pan, Kaydet)
        toolbar_frame = tk.Frame(bottom_frame, bg="#2b2b2b")
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def on_click(self, event):
        """Grafik üzerine sol (yakınlaş) veya sağ (uzaklaş) tıklama olayını yönetir."""
        if event.inaxes not in [self.ax1, self.ax2]: return
        
        # Kullanıcı manuel müdahale ettiği için otomatik ölçeklemeyi kapat
        self.auto_scale = False 
        
        if event.button == 1: 
            zoom_factor = 0.8
        elif event.button == 3: 
            zoom_factor = 1.2
        else: 
            return
            
        ax = event.inaxes
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        
        # Tıklanan noktayı merkez alarak yeni eksen sınırlarını hesapla
        ax.set_xlim([xdata + (x - xdata) * zoom_factor for x in xlim])
        ax.set_ylim([ydata + (y - ydata) * zoom_factor for y in ylim])
        self.canvas.draw_idle()

    def on_tree_double_click(self, event):
        """Tablodaki bir sıfıra çift tıklandığında grafikleri o noktaya odaklar."""
        item = self.tree.identify_row(event.y)
        if not item: return
        self.tree.selection_set(item)
        values = self.tree.item(item, 'values')
        
        try: 
            t_value = float(values[1])
        except: 
            return
            
        self.auto_scale = False
        self.ax1.set_ylim(t_value - 5, t_value + 5) 
        self.ax2.set_xlim(t_value - 100, t_value + 100)
        self.canvas.draw_idle()

    def log(self, msg, is_alarm=False):
        """Arayüzdeki log kutusuna mesaj yazar."""
        self.log_box.config(state=tk.NORMAL)
        if is_alarm:
            self.log_box.insert(tk.END, msg + "\n", "alarm")
        else:
            self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def start_scan(self):
        """Tarama işlemini başlatan thread'i tetikler."""
        if self.is_running: return
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="Durum: Taranıyor...", fg="#28a745")
        self.log("--- Tarama Başladı (Kritik Doğru + Re Testi) ---")
        self.auto_scale = True
        
        # Test değişkenlerini sıfırla
        self.test_re_index = 0
        self.test_t = 1.0
        
        # Arayüzün donmaması için taramayı arka plan thread'inde başlat
        self.thread = threading.Thread(target=self.scan_worker, daemon=True)
        self.thread.start()

    def stop_scan(self):
        """Tarama işlemini durdurur."""
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="Durum: Durduruldu", fg="#dc3545")
        self.log("--- Tarama Durduruldu ---")

    def scan_worker(self):
        """
        Arka planda çalışan ana tarama motoru.
        Aynı anda iki görevi yürütür:
        1. Kritik doğru (Re=0.5) üzerindeki sıfırları bulur.
        2. Re=0.5 dışındaki ihtimalleri test eder (Hipotez çürütme).
        """
        step = mp.mpf('0.5')
        
        while self.is_running:
            try:
                # --- GÖREV 1: KRİTİK DOĞRU TARAMASI (Re = 0.5) ---
                t = mp.mpf(self.current_t)
                
                # Riemann-Siegel Z fonksiyonu kullanılarak işaret değişimi kontrol edilir
                v1 = mp.siegelz(t)
                v2 = mp.siegelz(t + step)
                
                if v1 * v2 < 0:
                    self.root.after(0, self.log, f"[?] Çukur: {float(t):.2f}. Doğrulanıyor...")
                    
                    # Müller metodu ile sıfır noktası hassaslaştırılır
                    root = mp.findroot(mp.siegelz, t, solver='muller')
                    exact_t = float(root)
                    
                    if exact_t > self.last_found_t + 0.1:
                        # Zeta fonksiyonu ile hata payı testi
                        v_zeta = abs(mp.zeta(mp.mpc(0.5, exact_t)))
                        
                        if v_zeta < HATA_ESIGI:
                            self.last_found_t = exact_t
                            self.root.after(0, self.add_zero_to_ui, exact_t, float(v_zeta))
                            self.root.after(0, self.update_plots)
                            
                            time.sleep(0.1) # Arayüzün nefes alması için kısa bekleme
                            self.current_t = exact_t + 1.0
                            continue
                
                self.current_t += float(step)
                
                # --- GÖREV 2: GERÇEK KISIM (RE) TESTİ ---
                # Sistem performansını korumak için her 100 adımda bir test yapılır
                if int(self.current_t) % 100 == 0:
                    re = self.test_re_values[self.test_re_index]
                    test_val = abs(mp.zeta(mp.mpc(re, self.test_t)))
                    
                    self.root.after(0, self.update_ui_t, re)
                    
                    if test_val < HATA_ESIGI:
                        # Hipotezi çürütecek bir sıfır bulundu!
                        self.root.after(0, self.trigger_alarm, re, self.test_t, float(test_val))
                        return 
                    
                    self.test_t += 1.0 
                    
                    # Test döngüsünü yönet
                    if self.test_t > 10000:
                        self.test_t = 1.0
                        self.test_re_index += 1
                        if self.test_re_index >= len(self.test_re_values):
                            self.test_re_index = 0 
                            
            except Exception as e:
                # Beklenmeyen bir matematik hatasında döngünün kırılmamasını sağlar
                self.current_t += float(step)

    def trigger_alarm(self, re, t, hata):
        """Riemann Hipotezi'ni çürütecek bir sıfır bulunduğunda çalışır."""
        self.is_running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="!!! RİEMANN HİPOTEZİ ÇÖKTÜ !!!", fg="red")
        
        alarm_msg = f"\n{'='*40}\n"
        alarm_msg += f"🚨 BÜYÜK KEŞİF: HİPOTEZ YANLIŞ OLABİLİR 🚨\n"
        alarm_msg += f"Bulunan Sıfır: s = {re} + {t}i\n"
        alarm_msg += f"Hata Payı: {hata}\n"
        alarm_msg += f"{'='*40}\n"
        self.log(alarm_msg, is_alarm=True)
        
        messagebox.showinfo("TARİHİ AN!", f"Riemann Hipotezi Çürütüldü!\n\ns = {re} + {t}i\n\nLütfen bu durumu matematik camiasına bildirin!")

    def update_ui_t(self, re=None):
        """Anlık t değerini ve test edilen Re değerini ekrana yazar."""
        if re is not None:
            self.lbl_t.config(text=f"Kritik T: {self.current_t:.2f} | Test Re: {re}")
        else:
            self.lbl_t.config(text=f"Kritik T: {self.current_t:.2f}")

    def add_zero_to_ui(self, exact_t, hata):
        """Bulunan kesin sıfırı tabloya ekler ve arayüzü günceller."""
        self.found_zeros.append(exact_t)
        idx = len(self.found_zeros)
        t_str = mp.nstr(exact_t, 15)
        
        self.tree.insert("", tk.END, values=(idx, t_str, mp.nstr(hata, 3)))
        
        # Eğer kullanıcı tablonun en altındaysa otomatik aşağı kaydır
        if self.is_running and self.tree.yview()[1] >= 0.95:
            self.tree.yview_moveto(1)
            
        self.log(f"[✅] KESİN SIFIR: t = {t_str}")

    def update_plots(self):
        """Grafikleri yeni bulunan sıfırlarla günceller."""
        if not self.found_zeros: return
        
        self.scatter.set_data([0.5] * len(self.found_zeros), self.found_zeros)
        self.line_density.set_data(self.found_zeros, list(range(1, len(self.found_zeros) + 1)))
        
        # Otomatik ölçekleme aktifse eksen sınırlarını güncelle
        if self.auto_scale:
            y_min = min(self.found_zeros) - 10
            y_max = max(self.found_zeros) + 10
            if y_max - y_min < 50: y_max = y_min + 50
            self.ax1.set_ylim(y_min, y_max)
            
            x_min = min(self.found_zeros) - 10
            x_max = max(self.found_zeros) + 10
            if x_max - x_min < 100: x_max = x_min + 100
            self.ax2.set_xlim(x_min, x_max)
            self.ax2.set_ylim(0, len(self.found_zeros) + 2)
            
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = ZetaHunterApp(root)
    root.mainloop()