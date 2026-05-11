import customtkinter as ctk
import time
import threading
import subprocess
import random
import tkinter as tk

# Проверка наличия библиотеки OpenCL
try:
    import pyopencl as cl
    GLOBAL_OPENCL = True
except ImportError:
    GLOBAL_OPENCL = False

ctk.set_appearance_mode("dark")

class UltimateGPUBenchmark(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI CORE v6.6 - Ultimate Ranking Edition")
        self.geometry("950x750")
        self.current_color = "#FF4444"
        self.last_score = 0
        self.is_running = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Сайдбар
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
        mode = "HARDWARE (OpenCL)" if GLOBAL_OPENCL else "SOFTWARE (Legacy)"
        ctk.CTkLabel(self.main_container, text=mode, font=("Arial", 16, "bold"), text_color="gray").pack(pady=(0, 10))

        self.score_box = ctk.CTkFrame(self.main_container, fg_color="#111", corner_radius=20, height=220, border_width=2, border_color="#444")
        self.score_box.pack(fill="x", pady=20)
        self.score_box.pack_propagate(False)
        
        self.score_val = ctk.CTkLabel(self.score_box, text=str(self.last_score) if self.last_score > 0 else "READY", 
                                     font=("Consolas", 110, "bold"), text_color=self.current_color)
        self.score_val.place(relx=0.5, rely=0.5, anchor="center")

        self.bar = ctk.CTkProgressBar(self.main_container, width=600, height=20, progress_color=self.current_color)
        self.bar.set(0)
        self.bar.pack(pady=20)

        self.run_btn = ctk.CTkButton(self.main_container, text="START ENGINE TEST", height=70, 
                                    font=("Arial", 18, "bold"), fg_color="#CC0000", command=self.start_test)
        self.run_btn.pack(side="bottom", pady=20, fill="x")

    def start_test(self):
        if self.is_running: return
        self.is_running = True
        self.run_btn.configure(state="disabled", text="GPU WORKING...")
        threading.Thread(target=self.run_stress, daemon=True).start()

    def run_stress(self):
        duration = 15 
        start_time = time.time()
        iterations_done = 0
        use_opencl = GLOBAL_OPENCL
        
        if use_opencl:
            try:
                platforms = cl.get_platforms()
                gpu_device = None
                for plat in platforms:
                    devs = plat.get_devices(device_type=cl.device_type.GPU)
                    if devs:
                        gpu_device = devs[0]
                        break
                if not gpu_device: gpu_device = platforms[0].get_devices()[0]
                ctx = cl.Context([gpu_device])
                queue = cl.CommandQueue(ctx)
                
                kernel_code = """
                __kernel void stress(__global float *a) {
                  int i = get_global_id(0);
                  float val = a[i];
                  for(int n=0; n<8000; n++) { 
                      val = native_sqrt(val + (float)n) * native_sin(val + 0.1f); 
                  }
                  a[i] = val;
                }
                """
                prg = cl.Program(ctx, kernel_code).build()
                mem = cl.Buffer(ctx, cl.mem_flags.READ_WRITE, 10**6 * 4)
            except:
                use_opencl = False 

        while (time.time() - start_time) < duration:
            if not self.is_running: break
            
            if use_opencl:
                try: 
                    prg.stress(queue, (10**6,), None, mem)
                    queue.finish() 
                    iterations_done += 1
                except: 
                    use_opencl = False
            else:
                for _ in range(50): self.canvas.create_oval(0,0,1,1)
                self.canvas.delete("all")
                iterations_done += 0.05
                time.sleep(0.01)
            
            if iterations_done % 2 == 0:
                elapsed = time.time() - start_time
                progress = min(elapsed / duration, 1.0)
                try:
                    self.bar.set(progress)
                    self.score_val.configure(text=str(int(iterations_done * 215)))
                except: break

        self.last_score = int(iterations_done * 215)
        self.is_running = False
        try:
            self.run_btn.configure(state="normal", text="RE-RUN TEST")
            self.score_val.configure(text=str(self.last_score))
            self.bar.set(1.0)
        except: pass

    def get_hw(self, type):
        try:
            cmd = "wmic cpu get name" if type == "cpu" else "wmic path win32_VideoController get name"
            res = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').split('\n')
            return res[1].strip() if len(res) > 1 else "Unknown"
        except: return "Unknown"

    def show_stats(self):
        self.clear_content()
        ctk.CTkLabel(self.main_container, text="HARDWARE INFO", font=("Arial", 22, "bold")).pack(pady=20)
        gpu = self.get_hw("gpu")
        cpu = self.get_hw("cpu")
        for k, v in [("GPU UNIT", gpu), ("CPU UNIT", cpu), ("CORE", "6.6.0 FINAL")]:
            f = ctk.CTkFrame(self.main_container, fg_color="#111", height=50)
            f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=k, font=("Arial", 14, "bold"), text_color=self.current_color, padx=20).pack(side="left")
            ctk.CTkLabel(f, text=v, font=("Arial", 14), padx=20).pack(side="right")

    def show_ranking(self):
        self.clear_content()
        ctk.CTkLabel(self.main_container, text="GLOBAL GPU RANKING", font=("Arial", 22, "bold")).pack(pady=10)
        
        # Полный список с добавленными RTX 20-й серии
        rank = [
            ("RTX 5090 (Lush)", 1250000),
            ("RTX 4090", 980000),
            ("RTX 4080 Super", 740000),
            ("RTX 3090 Ti", 620000),
            ("RTX 4070 Ti", 510000),
            ("RTX 3080", 440000),
            ("RTX 2080 Ti", 380000), # Добавлено
            ("RTX 3070", 310000),
            ("RTX 2080 Super", 285000), # Добавлено
            ("RTX 4060", 240000),
            ("RTX 2070 Super", 215000), # Добавлено
            ("RTX 3060", 185000),
            ("RTX 2060 Super", 145000), # Добавлено
            ("GTX 1080 Ti", 115000),
            ("RTX 2060", 105000), # Добавлено
            ("YOU", self.last_score),
            ("GTX 1070", 72000),
            ("GTX 1650 Super", 58000),
            ("GTX 1050 Ti", 44000),
            ("GTX 1050", 31000),
            ("GTX 750 Ti", 12000)
        ]
        
        rank.sort(key=lambda x: x[1], reverse=True)
        
        sf = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", height=450)
        sf.pack(fill="both", expand=True)
        
        for n, s in rank:
            is_me = (n == "YOU")
            f = ctk.CTkFrame(sf, fg_color="#181818" if is_me else "#111", 
                            border_width=1 if is_me else 0, 
                            border_color=self.current_color if is_me else "white")
            f.pack(fill="x", pady=2)
            
            lbl_name = ctk.CTkLabel(f, text=n, padx=20, font=("Arial", 13, "bold" if is_me else "normal"),
                                   text_color=self.current_color if is_me else "white")
            lbl_name.pack(side="left")
            
            lbl_score = ctk.CTkLabel(f, text=f"{s:,} PTS".replace(',', ' '), padx=20, font=("Consolas", 14))
            lbl_score.pack(side="right")

if __name__ == "__main__":
    app = UltimateGPUBenchmark()
    app.mainloop()
