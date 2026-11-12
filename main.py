import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap, QAction
from PySide6.QtWidgets import *

RAW_EXTS = {".dng",".cr2",".cr3",".nef",".arw",".raf",".rw2",".orf",".pef",".srw",".3fr",".iiq",".kdc",".mos",".mrw",".nrw",".rwl",".x3f"}
FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff *.ico *.avif *.heic *.dng *.cr2 *.cr3 *.nef *.arw *.raf *.rw2 *.orf);;All files (*.*)"

def pixmap(im):
    im = im.convert("RGBA")
    q = QImage(im.tobytes(), im.width, im.height, im.width*4, QImage.Format_RGBA8888).copy()
    return QPixmap.fromImage(q)

class Fram(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fram — Photo Studio")
        self.resize(1120, 740)
        self.frames=[]; self.index=0; self.original=None; self.current=None; self.path=None
        self.setStyleSheet("""
        QMainWindow,QWidget{background:#f4f6fb;color:#252944;font-family:Segoe UI}
        QFrame#panel{background:white;border:1px solid #e4e7f0;border-radius:14px}
        QPushButton{background:white;border:1px solid #d9deeb;border-radius:9px;padding:9px}
        QPushButton:hover{background:#eeeaff;border-color:#aaa0ff}
        QPushButton#main{background:#6558e8;color:white;font-weight:bold}
        QLabel#muted{color:#788099}
        QComboBox,QSpinBox{background:white;border:1px solid #d9deeb;border-radius:7px;padding:6px}
        QSlider::groove:horizontal{height:6px;background:#e5e8f1;border-radius:3px}
        QSlider::handle:horizontal{background:#6558e8;width:14px;margin:-5px 0;border-radius:7px}
        """)
        bar=QToolBar(); bar.setMovable(False); self.addToolBar(bar)
        for label,fn in [("＋ Открыть",self.open_file),("Сохранить как",self.save_as),("↶ Сброс",self.reset),("−",self.zoom_out),("100%",self.zoom_reset),("＋",self.zoom_in)]:
            a=QAction(label,self); a.triggered.connect(fn); bar.addAction(a)
        root=QWidget(); self.setCentralWidget(root); layout=QVBoxLayout(root)
        head=QHBoxLayout(); title=QLabel("Fram"); title.setStyleSheet("font-size:28px;font-weight:800;color:#6558e8")
        head.addWidget(title); head.addWidget(QLabel("Просмотр • редактор • GIF • RAW")); head.addStretch()
        self.filename=QLabel("Файл не выбран"); self.filename.setObjectName("muted"); head.addWidget(self.filename); layout.addLayout(head)
        split=QSplitter(); layout.addWidget(split,1)
        left=QFrame(); left.setObjectName("panel"); lv=QVBoxLayout(left)
        self.canvas=QLabel("Открой изображение"); self.canvas.setAlignment(Qt.AlignCenter); self.canvas.setMinimumSize(420,360)
        self.canvas.setStyleSheet("background:#edf0f7;border-radius:10px;color:#8790a8;font-size:18px")
        lv.addWidget(self.canvas,1); self.info=QLabel("Поддержка зависит от формата и установленных кодеков"); self.info.setObjectName("muted"); lv.addWidget(self.info)
        nav=QHBoxLayout(); self.frameinfo=QLabel("Кадр —"); prev=QPushButton("◀ Кадр"); nxt=QPushButton("Кадр ▶")
        prev.clicked.connect(lambda:self.change_frame(-1)); nxt.clicked.connect(lambda:self.change_frame(1))
        nav.addWidget(self.frameinfo); nav.addStretch(); nav.addWidget(prev); nav.addWidget(nxt); lv.addLayout(nav); split.addWidget(left)
        side=QFrame(); side.setObjectName("panel"); side.setMinimumWidth(270); sv=QVBoxLayout(side)
        h=QLabel("Редактирование"); h.setStyleSheet("font-size:17px;font-weight:bold"); sv.addWidget(h)
        self.sliders={}
        for key,label in [("brightness","Яркость"),("contrast","Контраст"),("color","Насыщенность"),("sharpness","Резкость")]:
            sv.addWidget(QLabel(label)); sl=QSlider(Qt.Horizontal); sl.setRange(0,200); sl.setValue(100); sl.valueChanged.connect(self.apply)
            sv.addWidget(sl); self.sliders[key]=sl
        sv.addWidget(QLabel("Фильтр")); self.filters=QComboBox(); self.filters.addItems(["Оригинал","Чёрно-белый","Сепия","Негатив","Размытие","Рельеф"]); self.filters.currentIndexChanged.connect(self.apply); sv.addWidget(self.filters)
        for label,fn in [("Повернуть влево",lambda:self.rotate(90)),("Повернуть вправо",lambda:self.rotate(-90)),("Обрезать по центру",self.crop),("Изменить размер",self.resize_image),("Добавить текст",self.add_text),("Экспортировать GIF",self.export_gif)]:
            b=QPushButton(label); b.clicked.connect(fn); sv.addWidget(b)
        sv.addStretch(); save=QPushButton("Сохранить изменения"); save.setObjectName("main"); save.clicked.connect(self.save_as); sv.addWidget(save)
        split.addWidget(side); split.setSizes([800,300]); self.statusBar().showMessage("Готово")

    def open_file(self):
        p,_=QFileDialog.getOpenFileName(self,"Открыть изображение","",FILTER)
        if not p:return
        try:
            self.path=p; self.frames=[]
            if Path(p).suffix.lower() in RAW_EXTS:
                import rawpy
                with rawpy.imread(p) as raw: self.frames=[Image.fromarray(raw.postprocess()).convert("RGBA")]
            else:
                im=Image.open(p)
                for i in range(getattr(im,"n_frames",1)):
                    im.seek(i); self.frames.append(im.convert("RGBA").copy())
                im.close()
            self.index=0; self.original=self.frames[0].copy(); self.current=self.original.copy()
            self.filename.setText(Path(p).name); self.reset_controls(); self.show_image()
            self.statusBar().showMessage(f"Открыто: {p}")
        except Exception as e: QMessageBox.critical(self,"Не удалось открыть",str(e))
    def reset_controls(self):
        for s in self.sliders.values(): s.blockSignals(True); s.setValue(100); s.blockSignals(False)
        self.filters.blockSignals(True); self.filters.setCurrentIndex(0); self.filters.blockSignals(False)
    def show_image(self):
        if self.current is None:return
        self.canvas.setPixmap(pixmap(self.current).scaled(self.canvas.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.info.setText(f"{self.current.width} × {self.current.height} px")
        self.frameinfo.setText(f"Кадр {self.index+1} / {len(self.frames)}")
    def resizeEvent(self,e):
        super().resizeEvent(e)
        if self.current:self.show_image()
    def apply(self,*_):
        if self.original is None:return
        im=self.original.copy()
        for k,cls in [("brightness",ImageEnhance.Brightness),("contrast",ImageEnhance.Contrast),("color",ImageEnhance.Color),("sharpness",ImageEnhance.Sharpness)]:
            im=cls(im).enhance(self.sliders[k].value()/100)
        f=self.filters.currentIndex()
        if f==1: im=ImageOps.grayscale(im).convert("RGBA")
        elif f==2: im=ImageOps.colorize(ImageOps.grayscale(im),"#382313","#f5d49a").convert("RGBA")
        elif f==3: im=ImageOps.invert(im.convert("RGB")).convert("RGBA")
        elif f==4: im=im.filter(ImageFilter.GaussianBlur(2))
        elif f==5: im=im.filter(ImageFilter.EMBOSS)
        self.current=im; self.show_image()
    def change_frame(self,d):
        if not self.frames:return
        self.index=(self.index+d)%len(self.frames); self.original=self.frames[self.index].copy(); self.current=self.original.copy(); self.reset_controls(); self.show_image()
    def rotate(self,d):
        if self.current is None:return
        self.current=self.current.rotate(d,expand=True); self.original=self.current.copy(); self.frames[self.index]=self.current.copy(); self.show_image()
    def crop(self):
        if self.current is None:return
        w,h=self.current.size; nw,nh=int(w*.8),int(h*.8)
        self.current=self.current.crop(((w-nw)//2,(h-nh)//2,(w+nw)//2,(h+nh)//2)); self.original=self.current.copy(); self.frames[self.index]=self.current.copy(); self.show_image()
    def resize_image(self):
        if self.current is None:return
        w,ok=QInputDialog.getInt(self,"Размер","Новая ширина:",self.current.width,1,30000)
        if not ok:return
        h,ok=QInputDialog.getInt(self,"Размер","Новая высота:",self.current.height,1,30000)
        if ok:
            self.current=self.current.resize((w,h),Image.Resampling.LANCZOS); self.original=self.current.copy(); self.frames[self.index]=self.current.copy(); self.show_image()
    def add_text(self):
        if self.current is None:return
        t,ok=QInputDialog.getText(self,"Текст","Введите надпись:")
        if ok and t:
            im=self.current.convert("RGBA"); d=ImageDraw.Draw(im)
            try:f=ImageFont.truetype("arial.ttf",max(18,im.width//22))
            except:f=ImageFont.load_default()
            d.text((24,im.height-60),t,font=f,fill="white",stroke_width=2,stroke_fill="#333333")
            self.current=im; self.original=im.copy(); self.frames[self.index]=im.copy(); self.show_image()
    def reset(self):
        if self.original is not None:self.current=self.original.copy(); self.reset_controls(); self.show_image()
    def save_as(self):
        if self.current is None:return
        p,_=QFileDialog.getSaveFileName(self,"Сохранить как","Fram-edited.png","PNG (*.png);;JPEG (*.jpg *.jpeg);;WEBP (*.webp);;BMP (*.bmp);;TIFF (*.tiff)")
        if p:
            try:
                im=self.current.convert("RGB") if Path(p).suffix.lower() in (".jpg",".jpeg") else self.current
                im.save(p); self.statusBar().showMessage("Сохранено: "+p)
            except Exception as e:QMessageBox.critical(self,"Ошибка сохранения",str(e))
    def export_gif(self):
        if not self.frames:return
        p,_=QFileDialog.getSaveFileName(self,"Экспорт GIF","Fram.gif","GIF (*.gif)")
        if p:
            try:self.frames[0].save(p,save_all=True,append_images=self.frames[1:],duration=100,loop=0,disposal=2)
            except Exception as e:QMessageBox.critical(self,"Ошибка GIF",str(e))
    def zoom_in(self): self.canvas.resize(self.canvas.size()*1.2); self.show_image()
    def zoom_out(self): self.canvas.resize(self.canvas.size()*.8); self.show_image()
    def zoom_reset(self): self.canvas.adjustSize(); self.show_image()

if __name__=="__main__":
    app=QApplication(sys.argv); w=Fram(); w.show(); sys.exit(app.exec())
