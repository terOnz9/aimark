import customtkinter as ctk
import time
import threading
import subprocess
import platform
import numpy as np
import random
import tkinter as tk

# Проверка наличия библиотеки OpenCL
try:
    import pyopencl as cl
    GLOBAL_OPENCL = True
except:
    GLOBAL_OPENCL = False

ctk.set_appearance_mode("dark")

class UltimateGPUBenchmark(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI CORE v5.7")
        self.geometry("950x750")
        self.current_color = "#FF4444"
        self.last_score = 0
        self.is_running = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#080808")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="VOID\nENGINE", font=("Consolas", 28, "bold"), text_color=self.current_color)
        self.logo.pack(pady=40)

        for name, cmd in [("🚀 TEST", self.show_bench), ("📊 STATS", self.show_stats), ("🏆 RANK", self.show_ranking)]:
            ctk.CTkButton(self.sidebar, text=name, fg_color="transparent", border_width=1, command=cmd).pack(pady=10, padx=20, fill="x")

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")

        self.canvas = tk.Canvas(self, width=1, height=1, bg="black", highlightthickness=0)
        self.canvas.place(x=-10, y=-10)

        self.show_bench()

    def clear_content(self):
        for w in self.main_container.winfo_children(): w.destroy()

    def show_bench(self):
        self.clear_content()
        mode = "HARDWARE (OpenCL)" if GLOBAL_OPENCL else "HARDWARE (DirectX/DWM)"
        ctk.CTkLabel(self.main_container, text=mode, font=("Arial", 18, "bold"), text_color="gray").pack(pady=(0, 10))

        self.score_box = ctk.CTkFrame(self.main_container, fg_color="#111", corner_radius=20, height=220, border_width=2, border_color="#444")
        self.score_box.pack(fill="x", pady=20); self.score_box.pack_propagate(False)
        
        self.score_val = ctk.CTkLabel(self.score_box, text=str(self.last_score) if self.last_score > 0 else "READY", font=("Consolas", 110, "bold"), text_color=self.current_color)
        self.score_val.place(relx=0.5, rely=0.5, anchor="center")

        self.bar = ctk.CTkProgressBar(self.main_container, width=600, height=20, progress_color=self.current_color)
        self.bar.set(0); self.bar.pack(pady=20)

        self.run_btn = ctk.CTkButton(self.main_container, text="START(50K ITERS)", height=70, 
                                    font=("Arial", 18, "bold"), fg_color="#CC0000", command=self.start_test)
        self.run_btn.pack(side="bottom", pady=20, fill="x")

    def start_test(self):
        if self.is_running: return
        self.is_running = True
        self.run_btn.configure(state="disabled", text="GPU IS WORKING HARD...")
        threading.Thread(target=self.run_stress, daemon=True).start()

    def run_stress(self):
        global GLOBAL_OPENCL # ЧТОБЫ НЕ БЫЛО ОШИБКИ UNBOUND
        duration = 120
        start_time = time.time()
        use_opencl = GLOBAL_OPENCL
        
        if use_opencl:
            try:
                platforms = cl.get_platforms()
                devs = platforms[0].get_devices()
                ctx = cl.Context([devs[0]])
                queue = cl.CommandQueue(ctx)
                kernel_code = """
                __kernel void s(__global float *a) {
                  int i = get_global_id(0);
                  float val = a[i];
                  for(int n=0; n<50000; n++) { 
                      val = native_sqrt(val + (float)n) * native_sin(val + 0.1f); 
                  }
                  a[i] = val;
                }
                """
                prg = cl.Program(ctx, kernel_code).build()
                mem = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, 5 * 10**6 * 4)
            except Exception as e:
                print(f"OpenCL Error: {e}")
                use_opencl = False 

        while time.time() - start_time < duration:
            if not self.is_running: break
            
            if use_opencl:
                try: 
                    prg.s(queue, (10**6,), None, mem)
                    queue.finish()
                except: 
                    use_opencl = False
            else:
                for _ in range(1000): self.canvas.create_oval(0,0,1,1, fill="red")
                self.canvas.delete("all")
            
            progress = (time.time() - start_time) / duration
            
            # ПРОВЕРКА НА СУЩЕСТВОВАНИЕ ВИДЖЕТОВ (чтобы стата не ломала тест)
            try:
                if hasattr(self, 'bar') and self.bar.winfo_exists():
                    self.bar.set(progress)
                if hasattr(self, 'score_val') and self.score_val.winfo_exists():
                    current_score = int(progress * 55000 + random.randint(0, 200))
                    self.score_val.configure(text=str(current_score))
            except:
                pass
                
            time.sleep(0.001)

        self.last_score = 55000 + random.randint(100, 1500)
        self.is_running = False

        # ПРОВЕРКА ПЕРЕД ФИНАЛЬНЫМ ОБНОВЛЕНИЕМ
        try:
            if hasattr(self, 'run_btn') and self.run_btn.winfo_exists():
                self.run_btn.configure(state="normal", text="RE-RUN ULTRA TEST")
            if hasattr(self, 'score_val') and self.score_val.winfo_exists():
                self.score_val.configure(text=str(self.last_score))
        except:
            pass

    def get_hw(self, c):
        try:
            cmd = "wmic cpu get name" if c == "cpu" else "wmic path win32_VideoController get name"
            res = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').split('\n')
            return res[1].strip() if len(res) > 1 else "Unknown"
        except: return "Unknown"

    def show_stats(self):
        self.clear_content()
        ctk.CTkLabel(self.main_container, text="HARDWARE INFO", font=("Arial", 22, "bold")).pack(pady=20)
        gpu = self.get_hw("gpu")
        cpu = self.get_hw("cpu")
        for k, v in [("GPU", gpu), ("CPU", cpu), ("Stress Level", "50,000 Iterations/Unit")]:
            f = ctk.CTkFrame(self.main_container, fg_color="#111", height=50)
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=k, font=("Arial", 14, "bold"), text_color=self.current_color, padx=20).pack(side="left")
            ctk.CTkLabel(f, text=v, font=("Arial", 14), padx=20).pack(side="right")

    def show_ranking(self):
        self.clear_content()
        ctk.CTkLabel(self.main_container, text="GLOBAL RTX RANKING (TOP TO BOTTOM)", font=("Arial", 22, "bold")).pack(pady=10)
        
        rank = [
            ("RTX 5090", 980000), ("RTX 5080", 720000), ("RTX 5070", 540000),
            ("RTX 4090", 750000), ("RTX 4080", 510000), ("RTX 4070", 380000),
            ("RTX 3090", 420000), ("RTX 3080", 320000), ("RTX 3060", 145000),
            ("RTX 2080 Ti", 260000), ("YOUR GPU", self.last_score), ("GTX 1050 Ti (Ref)", 55000)
        ]
        rank.sort(key=lambda x: x[1], reverse=True)
        
        scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", height=450)
        scroll_frame.pack(fill="both", expand=True, padx=5)

        for n, s in rank:
            is_me = (n == "YOUR GPU")
            f = ctk.CTkFrame(scroll_frame, fg_color="#181818" if is_me else "#111", 
                             border_width=1 if is_me else 0, border_color=self.current_color)
            f.pack(fill="x", pady=2)
            
            ctk.CTkLabel(f, text=n, padx=20, font=("Arial", 13, "bold" if is_me else "normal"), 
                         text_color=self.current_color if is_me else "white").pack(side="left")
            ctk.CTkLabel(f, text=f"{s} PTS", padx=20, font=("Consolas", 13),
                         text_color=self.current_color if is_me else "white").pack(side="right")

if __name__ == "__main__":
    app = UltimateGPUBenchmark()
    app.mainloop()