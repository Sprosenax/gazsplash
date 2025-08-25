# 📱 gazsplash


A Python tool for **unpacking and repacking splash.img boot logos**.  
Supports Qualcomm-style `SPLASH!!` images with **RLE24 compression**.  

---

## ✨ Features
- 🗂 **Unpack** → Extracts all splash entries into `index0.bmp`, `index1.bmp`, …  
- 📦 **Pack** → Rebuilds a splash.img from sequential BMP files (`index0.bmp`, `index1.bmp`, …)  
- ✅ Safety checks → Ensures no missing indexes and all BMPs match resolution  
- 📱 Confirmed working on real devices  

---

## 🚀 Usage

### Unpack an image
```bash
python splashtool.py unpack splash.img
```
This will create:
```
index0.bmp
index1.bmp
...
```

### Pack back into a splash.img
```bash
python splashtool.py pack splash_new.img
```

⚠️ **Important:**  
- You must keep all `index*.bmp` files in sequence (no missing numbers).  
- All BMPs must have the same resolution.  

---

## 🛠 Requirements
- Python 3.8+  
- [Pillow](https://pypi.org/project/Pillow/) for BMP handling:
```bash
pip install pillow
```

---

## 📝 Notes
- Currently supports **RLE24 compressed** entries.  
- Typical format: `720x1440`, but other sizes should work.  
- Each splash.img may contain 1 or more entries (`index0`, `index1`, …).  

---

## 📱 Supported Devices
- ✅ [Your Device Name Here] (confirmed working)  
- More devices will be added as the community contributes!  

---

## 🤝 Contributing
Want to add support for your device?  

1. Open an **Issue** and attach your `splash.img`.  
2. Mention device name & resolution if known.  
3. We’ll extend the tool to support your format!  

---

## ⚖️ License
MIT License – free to use, modify, and share.  
