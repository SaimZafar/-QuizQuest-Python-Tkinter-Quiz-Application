import random
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
import time

class Quiz:
    def __init__(self, qffile="quiz_questions.txt"):
        self.qFile = qffile
        self.qs = self.loadqqs()
        self.score = 0
        self.asked = set()
        self.stats = defaultdict(int)
        self.curQ = None
        self.qList = []
        self.timeLeft = 180
        self.timerRun = False
        self.timerLbl = None
        self.root = tk.Tk()
        self.root.title("QuizQuest")
        self.root.geometry("850x700")
        self.colors = {
            'primary': '#4a6fa5',
            'secondary': '#7ec8e3',
            'accent': '#ff7e5f',
            'text': '#ffffff',
            'darkText': '#333333',
            'bgTop': '#1b3b6f',
            'bgBottom': '#7ec8e3',
            'cardBg': '#f8f9fa'
        }
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        self.mainCont = tk.Frame(self.canvas, bg='white')
        self.mainCont.place(relx=0.5, rely=0.5, anchor='center', width=800, height=650)
        self.rounded_shadow(self.mainCont, 800, 650)
        self.titleFont = ('Montserrat', 28, 'bold')
        self.qFont = ('Open Sans', 16)
        self.btnFont = ('Open Sans', 14, 'bold')
        self.timerFont = ('Open Sans', 16, 'bold')
        self.setsty()
        self.makewidgets()
        self.showwelc()
        self.root.mainloop()
    
    def drawgrad(self, c, c1, c2):
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 2 or h < 2:
            return
        step = 1 / h
        c.delete('grad')
        for i in range(h):
            r = int((1 - step * i) * int(c1[1:3], 16) + step * i * int(c2[1:3], 16))
            g = int((1 - step * i) * int(c1[3:5], 16) + step * i * int(c2[3:5], 16))
            b = int((1 - step * i) * int(c1[5:7], 16) + step * i * int(c2[5:7], 16))
            color = f"#{r:02x}{g:02x}{b:02x}"
            c.create_line(0, i, w, i, fill=color, tags='grad')

    def on_canvas_resize(self, event):
        self.drawgrad(self.canvas, self.colors['bgTop'], self.colors['bgBottom'])
        self.mainCont.place(relx=0.5, rely=0.5, anchor='center', width=800, height=650)

    def rounded_shadow(self, widget, w, h):
        x = (self.canvas.winfo_width() - w) // 2
        y = (self.canvas.winfo_height() - h) // 2
        shadow = self.canvas.create_rectangle(x+8, y+8, x+w+8, y+h+8, fill='#d1d9e6', outline='', tags='shadow')
        rect = self.canvas.create_rectangle(x, y, x+w, y+h, fill='', outline='', width=0, tags='maincont')

    def setsty(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.colors['bgTop'])
        self.style.configure('Main.TFrame', background='white')
        self.style.configure('TButton', font=self.btnFont, padding=10, background=self.colors['primary'], foreground='white', borderwidth=0, relief='flat')
        self.style.map('TButton', background=[('active', self.colors['secondary'])], foreground=[('active', 'white')])
        self.style.configure('Title.TLabel', font=self.titleFont, foreground=self.colors['primary'], background='white')
        self.style.configure('Question.TLabel', font=self.qFont, foreground=self.colors['darkText'], background='white', wraplength=700)
        self.style.configure('Horizontal.TProgressbar', troughcolor='#e9ecef', background=self.colors['accent'], bordercolor=self.colors['primary'])
        self.style.configure('TRadiobutton', font=self.qFont, foreground=self.colors['darkText'], background='white', indicatorcolor=self.colors['primary'], selectcolor='white')
    
    def makewidgets(self):
        self.header = ttk.Frame(self.mainCont, style='Main.TFrame')
        self.header.pack(fill=tk.X, padx=20, pady=20)
        self.titleLbl = ttk.Label(self.header, text="🧠 QuizQuest", style='Title.TLabel')
        self.titleLbl.pack()
        self.quitBtn = ttk.Button(self.header, text="❌ QUIT", style='TButton', command=self.root.quit)
        self.quitBtn.pack(side=tk.RIGHT, padx=10)
        self.scoreFrame = ttk.Frame(self.mainCont, style='Main.TFrame')
        self.scoreFrame.pack(fill=tk.X, padx=20, pady=5)
        self.timerLbl = ttk.Label(self.scoreFrame, text="⏱️ TIME: 03:00", style='Question.TLabel', foreground=self.colors['primary'])
        self.timerLbl.pack(side=tk.LEFT)
        self.scoreLbl = ttk.Label(self.scoreFrame, text="🏆 SCORE: 0000", style='Question.TLabel', foreground=self.colors['accent'])
        self.scoreLbl.pack(side=tk.RIGHT)
        self.progFrame = ttk.Frame(self.mainCont, style='Main.TFrame')
        self.progFrame.pack(fill=tk.X, padx=20, pady=15)
        self.progLbl = ttk.Label(self.progFrame, style='Question.TLabel', foreground=self.colors['primary'])
        self.progLbl.pack(side=tk.LEFT)
        self.prog = ttk.Progressbar(self.progFrame, orient=tk.HORIZONTAL, length=600, mode='determinate', style='Horizontal.TProgressbar')
        self.prog.pack(fill=tk.X, expand=True)
        self.mainFrame = ttk.Frame(self.mainCont, style='Main.TFrame')
        self.mainFrame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.welcomeLbl = ttk.Label(self.mainFrame, text="Welcome to QuizQuest!", style='Title.TLabel', foreground=self.colors['primary'])
        self.descLbl = tk.Label(self.mainFrame, text="Test your knowledge with this beautifully designed quiz!\n10 questions • 3 minutes timer", font=self.qFont, fg=self.colors['darkText'], bg='white', justify='center')
        self.setFrame = ttk.Frame(self.mainFrame, style='Main.TFrame')
        self.numQLbl = ttk.Label(self.setFrame, text="Number of Questions:", style='Question.TLabel')
        self.numQSpin = tk.Spinbox(self.setFrame, from_=1, to=50, width=5, font=self.qFont)
        self.numQSpin.delete(0, 'end')
        self.numQSpin.insert(0, '10')
        self.timerLblSet = ttk.Label(self.setFrame, text="Timer (minutes):", style='Question.TLabel')
        self.timerSpin = tk.Spinbox(self.setFrame, from_=1, to=30, width=5, font=self.qFont)
        self.timerSpin.delete(0, 'end')
        self.timerSpin.insert(0, '3')
        self.startBtn = ttk.Button(self.mainFrame, text="🚀 START QUIZ", style='TButton', command=self.stquiz)
        self.qCard = ttk.Frame(self.mainFrame, style='Main.TFrame', borderwidth=2, relief='solid', padding=20)
        self.qLbl = ttk.Label(self.qCard, style='Question.TLabel', foreground=self.colors['darkText'])
        self.choiceVar = tk.IntVar()
        self.choices = []
        for i in range(4):
            rb = tk.Radiobutton(self.qCard, variable=self.choiceVar, value=i, font=self.qFont, fg=self.colors['darkText'], bg='white', activebackground=self.colors['secondary'], selectcolor=self.colors['primary'])
            self.choices.append(rb)
        self.resCard = ttk.Frame(self.mainFrame, style='Main.TFrame', padding=20)
        self.resLbl = ttk.Label(self.resCard, style='Title.TLabel', foreground=self.colors['accent'])
        self.statsLbl = tk.Text(self.resCard, font=('Open Sans', 14), wrap=tk.WORD, padx=20, pady=20, height=10, width=60, bg='white', fg=self.colors['darkText'], borderwidth=0, highlightthickness=0)
        self.btnFrame = ttk.Frame(self.resCard, style='Main.TFrame')
        self.restartBtn = ttk.Button(self.btnFrame, text="🔄 PLAY AGAIN", style='TButton', command=self.showwelc)
        self.repeatBtn = ttk.Button(self.btnFrame, text="🔁 REPEAT QUIZ", style='TButton', command=self.repquiz)
        self.reviewBtn = ttk.Button(self.btnFrame, text="📝 REVIEW ANSWERS", style='TButton', command=self.showreview)
    
    def loadqqs(self):
        qs = []
        try:
            with open(self.qFile, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|')
                        if len(parts) >= 6:
                            cat = parts[0].strip()
                            diff = parts[1].strip()
                            txt = parts[2].strip()
                            chs = [c.strip() for c in parts[3:7]]
                            try:
                                corr = int(parts[7].strip()) - 1
                            except (ValueError, IndexError):
                                corr = 0
                            expl = parts[8].strip() if len(parts) > 8 else ""
                            qs.append(Q(cat, diff, txt, chs, corr, expl))
        except FileNotFoundError:
            messagebox.showerror("Error", f"Question file '{self.qFile}' not found!")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Error loading questions: {str(e)}")
            return []
        return qs
    
    def updatetimer(self):
        if not self.timerRun or self.timeLeft <= 0:
            if self.timeLeft <= 0:
                self.timeup()
            return
        self.timeLeft -= 1
        m = self.timeLeft // 60
        s = self.timeLeft % 60
        self.timerLbl.config(text=f"⏱️ TIME: {m:02d}:{s:02d}")
        self.root.after(1000, self.updatetimer)
   
    def timeup(self):
        self.timerRun = False
        messagebox.showinfo("Time's Up!", "Your time has run out! Let's see your results.")
        self.showres()
    
    def showwelc(self):
        for w in self.mainFrame.winfo_children():
            w.pack_forget()
        self.welcomeLbl.pack(pady=(40, 10))
        self.descLbl.pack(pady=20)
        self.setFrame.pack(pady=10)
        self.numQLbl.pack(side=tk.LEFT, padx=5)
        self.numQSpin.pack(side=tk.LEFT, padx=5)
        self.timerLblSet.pack(side=tk.LEFT, padx=5)
        self.timerSpin.pack(side=tk.LEFT, padx=5)
        self.startBtn.pack(pady=40)
        self.score = 0
        self.asked = set()
        self.stats.clear()
        self.timeLeft = 180
        self.timerLbl.config(text="⏱️ TIME: 03:00")
        self.updatescore()
   
    def repquiz(self):
        self.showwelc()
        self.stquiz()
    
    def stquiz(self):
        for w in self.mainFrame.winfo_children():
            w.pack_forget()
        try:
            nQ = int(self.numQSpin.get())
        except Exception:
            nQ = 10
        try:
            tMin = int(self.timerSpin.get())
        except Exception:
            tMin = 3
        self.timeLeft = tMin * 60
        self.nQ = min(nQ, len(self.qs))
        self.qList = random.sample(self.qs, self.nQ)
        self.asked = set()
        self.score = 0
        self.stats.clear()
        self.updatescore()
        self.timerRun = True
        self.updatetimer()
        self.nextq()
    
    def nextq(self):
        for w in self.qCard.winfo_children():
            w.pack_forget()
        self.choiceVar.set(-1)
        if len(self.asked) >= getattr(self, 'nQ', 10):
            self.timerRun = False
            self.showres()
            return
        avail = [q for q in self.qList if q not in self.asked]
        if not avail:
            self.timerRun = False
            self.showres()
            return
        self.curQ = random.choice(avail)
        self.asked.add(self.curQ)
        progVal = (len(self.asked) / getattr(self, 'nQ', 10)) * 100
        self.prog['value'] = progVal
        self.progLbl.config(text=f"📝 QUESTION {len(self.asked)}/{getattr(self, 'nQ', 10)}")
        self.qCard.pack(fill=tk.BOTH, expand=True, pady=10)
        qTxt = f"💡 {self.curQ.text}"
        self.qLbl.config(text=qTxt)
        self.qLbl.pack(anchor='w', pady=(0, 20))
        chs = self.curQ.choices.copy()
        corrIdx = self.curQ.correctAnswer
        corrAns = chs[corrIdx]
        random.shuffle(chs)
        self.curQ.correctAnswer = chs.index(corrAns)
        for i, c in enumerate(chs):
            self.choices[i].config(text=f"   {chr(65 + i)}. {c}")
            self.choices[i].pack(anchor='w', pady=5, padx=20)
        ttk.Button(self.qCard, text="📤 SUBMIT ANSWER", style='TButton', command=self.submitans).pack(pady=20)
    
    def show_notification(self, message, color='#4a6fa5', duration=1800):
        if hasattr(self, '_notif_box') and self._notif_box.winfo_exists():
            self._notif_box.destroy()
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes('-topmost', True)
        notif.configure(bg='white')
        notif.lift()
        notif.update_idletasks()
        w, h = 420, 220 
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        notif.geometry(f'{w}x{h}+{x}+{y}')
        border_color = color if color else self.colors['primary']
        border_frame = tk.Frame(notif, bg=border_color, bd=0, highlightthickness=0)
        border_frame.pack(fill=tk.BOTH, expand=True)
        frame = tk.Frame(border_frame, bg='white', bd=0, highlightthickness=0)
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        label = tk.Label(frame, text=message, font=('Open Sans', 15, 'bold'), fg=color, bg='white', wraplength=380, justify='center')
        label.pack(expand=True, padx=20, pady=20)
        notif.after(duration, notif.destroy)
        self._notif_box = notif
    
    def submitans(self):
        if self.choiceVar.get() == -1:
            self.show_notification("⚠️ Please select an answer!", color='#ff7e5f', duration=1500)
            return
        ans = self.choiceVar.get()
        corr = self.curQ.correctAnswer
        self.curQ.userAnswer = ans
        if ans == corr:
            self.score += 10
            self.stats[self.curQ.difficulty] += 1
            msg = f"✅ Correct!\n\n{self.curQ.explanation}\n\n+10 points!"
            self.show_notification(msg, color='#2ecc71', duration=1800)
        else:
            corrLetter = chr(65 + corr)
            corrAns = self.curQ.choices[corr]
            msg = f"❌ Incorrect\n\nThe correct answer was {corrLetter}. {corrAns}\n\n{self.curQ.explanation}"
            self.show_notification(msg, color='#e74c3c', duration=2200)
        self.updatescore()
        self.nextq()
    
    def updatescore(self):
        self.scoreLbl.config(text=f"🏆 SCORE: {self.score:04d}")
   
    def showres(self):
        for w in self.mainFrame.winfo_children():
            w.pack_forget()
        self.resCard.pack(fill=tk.BOTH, expand=True)
        corr = sum(self.stats.values())
        total = len(self.asked)
        acc = (corr / total) * 100 if total > 0 else 0
        tTaken = (getattr(self, 'nQ', 10) * getattr(self, 'timeLeft', 180) // getattr(self, 'nQ', 10)) - self.timeLeft
        m = tTaken // 60
        s = tTaken % 60
        resTxt = (f"⏱️ Time taken: {m:02d}m {s:02d}s\n\n"
                  f"🏅 Final Score: {self.score}/{self.nQ * 10}\n"
                  f"🎯 Accuracy: {acc:.1f}% ({corr}/{total})\n\n"
                  "📊 Breakdown by Difficulty:\n")
        for d in ['Easy', 'Medium', 'Hard']:
            cnt = self.stats.get(d, 0)
            tInD = len([q for q in self.qList if q.difficulty == d])
            if tInD > 0:
                pct = (cnt / tInD) * 100
                resTxt += (f"  {d.upper()}: {cnt}/{tInD} " f"({pct:.1f}%)\n")
        self.resLbl.config(text="🌟 Quiz Results!")
        self.resLbl.pack()
        self.statsLbl.config(state=tk.NORMAL)
        self.statsLbl.delete('1.0', tk.END)
        self.statsLbl.insert(tk.END, resTxt)
        self.statsLbl.config(state=tk.DISABLED)
        self.statsLbl.pack(pady=10)
        self.btnFrame.pack(pady=20)
        self.restartBtn.pack(side=tk.LEFT, padx=10)
        self.repeatBtn.pack(side=tk.LEFT, padx=10)
        self.reviewBtn.pack(side=tk.LEFT, padx=10)
    
    def showreview(self):
        win = tk.Toplevel(self.root)
        win.title("Review Answers")
        win.geometry("800x600")
        txt = tk.Text(win, font=('Open Sans', 13), wrap=tk.WORD, padx=20, pady=20, bg='white', fg=self.colors['darkText'])
        txt.pack(fill=tk.BOTH, expand=True)
        for idx, q in enumerate(self.qList):
            userAns = None
            for aQ in self.asked:
                if aQ.text == q.text:
                    userAns = aQ.choices[getattr(aQ, 'userAnswer', -1)] if hasattr(aQ, 'userAnswer') and getattr(aQ, 'userAnswer', -1) >= 0 else 'No answer'
                    break
            corrLetter = chr(65 + q.correctAnswer)
            corrAns = q.choices[q.correctAnswer]
            txt.insert(tk.END, f"Q{idx+1}: {q.text}\n")
            txt.insert(tk.END, f"  Your answer: {userAns}\n")
            txt.insert(tk.END, f"  Correct answer: {corrLetter}. {corrAns}\n")
            txt.insert(tk.END, f"  Explanation: {q.explanation}\n\n")
        txt.config(state=tk.DISABLED)

class Q:
    def __init__(self, cat, diff, text, chs, corrAns, expl):
        self.category = cat
        self.difficulty = diff
        self.text = text
        self.choices = chs
        self.correctAnswer = corrAns
        self.explanation = expl

if __name__ == "__main__":
    quiz = Quiz()
