# PowerK - Home Assistant Integration (المشترك الكوري MTTL-W01)

إضافة مخصصة (Custom Component) لربط المشترك الذكي الكوري (**LG U+ / Jinheung / TCL MTTL-W01**) بنظام **Home Assistant** بالاعتماد على مشروع [ahmedtohamy1/powerk](https://github.com/ahmedtohamy1/powerk).

---

## 🌟 المميزات المتاحة (Features)

* **التحكم المستقل بالمخارج (Independent Outlet Control):**
  * `switch.korean_smart_strip_outlet_1` (المخرج 1)
  * `switch.korean_smart_strip_outlet_2` (المخرج 2)
  * `switch.korean_smart_strip_outlet_3` (المخرج 3)
  * `switch.korean_smart_strip_outlet_4` (المخرج 4)
  * `switch.korean_smart_strip_all_outlets` (مفتاح رئيسي للتشغيل/الإيقاف الكامل)
* **مستشعرات الطاقة المتقدمة (Power & Energy Monitoring):**
  * `sensor.korean_smart_strip_power` (الوات اللحظي W)
  * `sensor.korean_smart_strip_total_energy` (الاستهلاك التراكمي بالكيلووات kWh) - **متوافق بالكامل مع HA Energy Dashboard**.
  * `sensor.korean_smart_strip_voltage` (الجهد الكهربائي الفعلي V)
  * `sensor.korean_smart_strip_temperature` (درجة الحرارة الداخلية للبوردة °C للأمان)
  * `sensor.korean_smart_strip_wifi_signal` (قوة إشارة الوايفاي)
* **حالة الاتصال (Binary Sensor):**
  * `binary_sensor.korean_smart_strip_connection_status` (Online / Offline)
* **إعداد مرئي كامل (UI Config Flow):** يتم إضافة المشترك مباشرة من واجهة هوم اسيستنت دون تعديل أي ملفات YAML.
* **واجهة ثنائية اللغة:** دعم كامل للغتين العربية والإنجليزية.

---

## 🚀 طريقة التثبيت في Home Assistant (Installation)

### الطريقة اليدوية (Manual Install):
1. انسخ مجلد `custom_components/powerk` إلى مجلد إعدادات هوم اسيستنت داخل المسار:
   ```text
   /config/custom_components/powerk
   ```
2. أعد تشغيل Home Assistant من **Developer Tools -> Restart**.

---

## ⚙️ طريقة الربط والإعداد (Configuration)

1. تأكد من تشغيل سيرفر `powerk.py` على أي جهاز في شبكتك المحلية (أو سيرفر منزلي):
   ```bash
   python3 powerk.py serve --web-port 7896 --token YOUR_TOKEN
   ```
2. ادخل إلى **Home Assistant** ثم توجه إلى:
   * **Settings (الإعدادات)** > **Devices & Services (الأجهزة والخدمات)**.
   * اضغط على **Add Integration (إضافة تكامل)**.
   * ابحث عن **PowerK Korean Smart Strip**.
3. أدخل البيانات:
   * **Host / IP Address:** عنوان الـ IP للجهاز المشغل لـ `powerk.py` (مثال: `192.168.1.50`).
   * **Port:** منفذ الويب (الافتراضي `7896`).
   * **Token:** رمز التحقق في حال كنت مفعله (أو اتركه فارغاً إذا لم تحدده).
4. اضغط **Submit**، وسيقوم هوم اسيستنت باكتشاف المشترك والـ MAC Address وإنشاء جميع الكيانات والمستشعرات تلقائياً!

---

## ⚡ الربط مع لوحة الطاقة (Energy Dashboard)

لاستعراض استهلاك المشترك في صفحة الطاقة الرسمية لـ Home Assistant:
1. اذهب إلى **Settings > Dashboards > Energy**.
2. تحت قسم **Individual devices**، اضغط **Add device**.
3. اختر المستشعر: `sensor.korean_smart_strip_total_energy`.
4. مبروك! سيتم تتبع استهلاك المشترك وتكلفة الكهرباء يومياً وأسبوعياً وشهرياً.

---

## 🛡️ رخصة ومصادر
هذا التكامل متوافق ومبني للعمل بتناغم مع مشروع [powerk](https://github.com/ahmedtohamy1/powerk).
