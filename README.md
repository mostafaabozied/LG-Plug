# LG-Plug - Home Assistant Integration

إضافة مخصصة (Custom Component) لربط المشترك الذكي (**LG MTTL-W01**) بنظام **Home Assistant**.

---

## 🌟 المميزات المتاحة (Features)

* **التحكم المستقل بالمخارج (Independent Outlet Control):**
  * `switch.lg_plug_outlet_1` (المخرج 1)
  * `switch.lg_plug_outlet_2` (المخرج 2)
  * `switch.lg_plug_outlet_3` (المخرج 3)
  * `switch.lg_plug_outlet_4` (المخرج 4)
  * `switch.lg_plug_all_outlets` (مفتاح رئيسي للتشغيل/الإيقاف الكامل)
* **مستشعرات الطاقة المتقدمة (Power & Energy Monitoring):**
  * `sensor.lg_plug_power` (الوات اللحظي W)
  * `sensor.lg_plug_total_energy` (الاستهلاك التراكمي بالكيلووات kWh) - **متوافق بالكامل مع HA Energy Dashboard**.
  * `sensor.lg_plug_voltage` (الجهد الكهربائي الفعلي V)
  * `sensor.lg_plug_temperature` (درجة الحرارة الداخلية للبوردة °C)
  * `sensor.lg_plug_wifi_signal` (قوة إشارة الوايفاي)
* **حالة الاتصال (Binary Sensor):**
  * `binary_sensor.lg_plug_connection_status` (Online / Offline)
* **إعداد مرئي كامل (UI Config Flow):** يتم إضافة المشترك مباشرة من واجهة هوم اسيستنت دون تعديل أي ملفات YAML.
* **واجهة ثنائية اللغة:** دعم كامل للغتين العربية والإنجليزية.

---

## 🚀 طريقة التثبيت في Home Assistant (Installation)

### الطريقة الأولى: عبر HACS (المتجر)
1. افتح **HACS** > **Custom repositories**.
2. أضف رابط المستودع الخاص بك:
   ```text
   https://github.com/mostafaabozied/LG-Plug
   ```
3. اختر الفئة **Integration** واضغط **Download**.
4. أعد تشغيل Home Assistant.

### الطريقة الثانية: التثبيت اليدوي (Manual Install)
1. انسخ مجلد `custom_components/lg_plug` إلى مجلد إعدادات هوم اسيستنت داخل المسار:
   ```text
   /config/custom_components/lg_plug
   ```
2. أعد تشغيل Home Assistant من **Developer Tools -> Restart**.

---

## ⚙️ طريقة الربط والإعداد (Configuration)

1. ادخل إلى **Home Assistant** ثم توجه إلى:
   * **Settings (الإعدادات)** > **Devices & Services (الأجهزة والخدمات)**.
   * اضغط على **Add Integration (إضافة تكامل)**.
   * ابحث عن **LG-Plug**.
2. أدخل البيانات:
   * **Host / IP Address:** عنوان الـ IP للجهاز أو السيرفر.
   * **Port:** رقم المنفذ (الافتراضي `7896`).
   * **Token:** رمز التحقق في حال كنت مفعله (أو اتركه فارغاً إذا لم تحدده).
3. اضغط **Submit**، وسيقوم هوم اسيستنت باكتشاف المشترك والـ MAC Address وإنشاء جميع الكيانات والمستشعرات تلقائياً!

---

## ⚡ الربط مع لوحة الطاقة (Energy Dashboard)

لاستعراض استهلاك المشترك في صفحة الطاقة الرسمية لـ Home Assistant:
1. اذهب إلى **Settings > Dashboards > Energy**.
2. تحت قسم **Individual devices**، اضغط **Add device**.
3. اختر المستشعر: `sensor.lg_plug_total_energy`.
4. سيتم تتبع استهلاك المشترك وتكلفة الكهرباء يومياً وأسبوعياً وشهرياً.
