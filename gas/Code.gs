// ════════════════════════════════════════════════════════════
//  魏世芬聲音教練｜課程收費系統  —  Google Apps Script 後端
//  Sheets: 課程主檔 | 訂單主檔 | 付款明細
// ════════════════════════════════════════════════════════════

const SHEET = {
  COURSES:  '課程主檔',
  ORDERS:   '訂單主檔',
  PAYMENTS: '付款明細',
};

// ── 前台網頁入口 ──────────────────────────────────────────────
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('魏世芬聲音教練｜課程報名')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// ── 初始化試算表結構 ──────────────────────────────────────────
function initSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 課程主檔
  let sh = ss.getSheetByName(SHEET.COURSES);
  if (!sh) {
    sh = ss.insertSheet(SHEET.COURSES);
    sh.appendRow(['課程ID','課程名稱','課程類型','課程說明','圖示','單價','計費單位','是否開放','精選標記','建立時間']);
    sh.setFrozenRows(1);
    // 預設課程範例
    const now = _now();
    sh.appendRow(['C001','一對一私人課程','One-on-One','量身打造的專屬訓練，老師全程專注你的聲音問題，最快見效。','🎤',3000,'堂',true,true,now]);
    sh.appendRow(['C002','小班團體課程','Small Group','4人以下精緻小班，互相學習，在真實互動中突破說話侷限。','👥',5000,'期',true,false,now]);
    sh.appendRow(['C003','線上影音課程','Online Course','突破地域限制，隨時隨地自主學習，系統化聲音訓練課程。','💻',2800,'期',true,false,now]);
  }

  // 訂單主檔
  sh = ss.getSheetByName(SHEET.ORDERS);
  if (!sh) {
    sh = ss.insertSheet(SHEET.ORDERS);
    sh.appendRow(['訂單編號','報名時間','姓名','手機','Email','課程ID','課程名稱','應付金額','備註','訂單狀態','最後更新']);
    sh.setFrozenRows(1);
  }

  // 付款明細
  sh = ss.getSheetByName(SHEET.PAYMENTS);
  if (!sh) {
    sh = ss.insertSheet(SHEET.PAYMENTS);
    sh.appendRow(['付款ID','訂單編號','付款時間','付款方式','帳號後5碼','實付金額','備註','核對狀態','核對時間','核對備註']);
    sh.setFrozenRows(1);
  }

  return { ok: true };
}

// ════════════════════════════════════════════════════════════
//  前台 API
// ════════════════════════════════════════════════════════════

// 取得開放中的課程清單
function getPublicCourses() {
  try {
    const rows = _readSheet(SHEET.COURSES);
    return rows
      .filter(r => r['是否開放'] === true)
      .map(r => ({
        id:       r['課程ID'],
        name:     r['課程名稱'],
        type:     r['課程類型'],
        desc:     r['課程說明'],
        icon:     r['圖示'],
        price:    r['單價'],
        unit:     r['計費單位'],
        featured: r['精選標記'] === true,
      }));
  } catch(e) {
    return [];
  }
}

// 學員報名
function submitEnrollment(data) {
  const lock = LockService.getScriptLock();
  try { lock.waitLock(10000); } catch(e) {
    return { ok: false, msg: '系統繁忙，請稍後再試' };
  }

  try {
    const ss   = SpreadsheetApp.getActiveSpreadsheet();
    const oSh  = ss.getSheetByName(SHEET.ORDERS);
    const now  = new Date();
    const orderId = 'VF-' + Utilities.formatDate(now,'Asia/Taipei','yyyyMMddHHmmss')
                  + '-' + data.phone.slice(-3);
    const ts   = _fmt(now);

    // 驗證課程存在
    const courses = getPublicCourses();
    const course  = courses.find(c => c.id === data.courseId);
    if (!course) return { ok: false, msg: '找不到指定課程' };

    oSh.appendRow([
      orderId, ts,
      data.name, _cleanPhone(data.phone), data.email || '',
      data.courseId, course.name, course.price,
      data.note || '', '待付款', ts
    ]);

    return { ok: true, orderId, courseName: course.name, amount: course.price };
  } catch(e) {
    Logger.log(e);
    return { ok: false, msg: '系統錯誤：' + e.toString() };
  } finally {
    lock.releaseLock();
  }
}

// 學員查詢訂單
function queryByPhone(phone) {
  try {
    const cleanInput = _normalizePhone(phone);
    const orders  = _readSheet(SHEET.ORDERS);
    const payments = _readSheet(SHEET.PAYMENTS);

    const matched = orders.filter(o => _normalizePhone(String(o['手機'])) === cleanInput);
    if (matched.length === 0) return { ok: true, count: 0, orders: [] };

    const result = matched.map(o => {
      const pays = payments.filter(p => p['訂單編號'] === o['訂單編號']);
      const pay  = pays[0] || null;
      return {
        orderId:    o['訂單編號'],
        timestamp:  _fmtDisplay(o['報名時間']),
        name:       o['姓名'],
        phone:      o['手機'],
        courseId:   o['課程ID'],
        courseName: o['課程名稱'],
        amount:     o['應付金額'],
        status:     o['訂單狀態'],
        payment: pay ? {
          method:   pay['付款方式'],
          account:  pay['帳號後5碼'],
          paidAmt:  pay['實付金額'],
          verified: pay['核對狀態'],
        } : null,
      };
    });

    result.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
    return { ok: true, count: result.length, orders: result };
  } catch(e) {
    Logger.log(e);
    return { ok: false, msg: '查詢錯誤：' + e.toString() };
  }
}

// 學員補填付款資料
function submitPayment(data) {
  const lock = LockService.getScriptLock();
  try { lock.waitLock(8000); } catch(e) {
    return { ok: false, msg: '系統繁忙，請稍後再試' };
  }

  try {
    const ss   = SpreadsheetApp.getActiveSpreadsheet();
    const oSh  = ss.getSheetByName(SHEET.ORDERS);
    const pSh  = ss.getSheetByName(SHEET.PAYMENTS);
    const now  = new Date();
    const ts   = _fmt(now);

    // 確認訂單存在且屬於該手機
    const orders = _readSheet(SHEET.ORDERS);
    const order  = orders.find(o =>
      o['訂單編號'] === data.orderId &&
      _normalizePhone(String(o['手機'])) === _normalizePhone(data.phone)
    );
    if (!order) return { ok: false, msg: '找不到訂單或手機不符' };

    // 確認尚未填寫
    const existing = _readSheet(SHEET.PAYMENTS).find(p => p['訂單編號'] === data.orderId);
    if (existing) return { ok: false, msg: '此訂單已有付款記錄，如需修改請聯繫老師' };

    // 寫入付款明細
    const payId = 'PAY-' + Utilities.formatDate(now,'Asia/Taipei','yyyyMMddHHmmss');
    pSh.appendRow([
      payId, data.orderId, ts,
      data.method, data.account || '', data.amount,
      data.note || '', '待核對', '', ''
    ]);

    // 更新訂單狀態
    const oData = oSh.getDataRange().getValues();
    for (let i = 1; i < oData.length; i++) {
      if (oData[i][0] === data.orderId) {
        oSh.getRange(i+1, 10).setValue('待對帳');
        oSh.getRange(i+1, 11).setValue(ts);
        break;
      }
    }

    return { ok: true, msg: '付款資料已送出，待老師確認！' };
  } catch(e) {
    Logger.log(e);
    return { ok: false, msg: '系統錯誤：' + e.toString() };
  } finally {
    lock.releaseLock();
  }
}

// ════════════════════════════════════════════════════════════
//  後台 API（供 Streamlit 透過 fetch 呼叫，需驗證 token）
// ════════════════════════════════════════════════════════════

const ADMIN_TOKEN = PropertiesService.getScriptProperties().getProperty('ADMIN_TOKEN') || 'changeme';

function doPost(e) {
  try {
    const body   = JSON.parse(e.postData.contents);
    const { action, token, payload } = body;

    if (token !== ADMIN_TOKEN) {
      return _json({ ok: false, msg: 'Unauthorized' });
    }

    const handlers = {
      getCourses:    () => ({ ok: true, data: _readSheet(SHEET.COURSES) }),
      saveCourse:    () => _adminSaveCourse(payload),
      deleteCourse:  () => _adminDeleteCourse(payload),
      getOrders:     () => _adminGetOrders(payload),
      getPayments:   () => ({ ok: true, data: _readSheet(SHEET.PAYMENTS) }),
      verifyPayment: () => _adminVerifyPayment(payload),
      updateOrder:   () => _adminUpdateOrder(payload),
      getDashboard:  () => _adminDashboard(),
    };

    if (!handlers[action]) return _json({ ok: false, msg: 'Unknown action' });
    return _json(handlers[action]());
  } catch(e) {
    return _json({ ok: false, msg: e.toString() });
  }
}

// 後台：取得訂單（含篩選）
function _adminGetOrders(p) {
  let orders   = _readSheet(SHEET.ORDERS);
  let payments = _readSheet(SHEET.PAYMENTS);

  if (p && p.status) orders = orders.filter(o => o['訂單狀態'] === p.status);
  if (p && p.courseId) orders = orders.filter(o => o['課程ID'] === p.courseId);
  if (p && p.keyword) {
    const kw = p.keyword.toLowerCase();
    orders = orders.filter(o =>
      String(o['姓名']).includes(kw) ||
      String(o['手機']).includes(kw) ||
      String(o['訂單編號']).toLowerCase().includes(kw)
    );
  }

  const result = orders.map(o => {
    const pay = payments.find(p => p['訂單編號'] === o['訂單編號']) || null;
    return { ...o, payment: pay };
  });

  result.sort((a,b) => new Date(b['報名時間']) - new Date(a['報名時間']));
  return { ok: true, data: result };
}

// 後台：新增 / 更新課程
function _adminSaveCourse(p) {
  const ss  = SpreadsheetApp.getActiveSpreadsheet();
  const sh  = ss.getSheetByName(SHEET.COURSES);
  const now = _now();

  if (p.id) {
    // 更新
    const data = sh.getDataRange().getValues();
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === p.id) {
        sh.getRange(i+1, 1, 1, 10).setValues([[
          p.id, p.name, p.type, p.desc, p.icon,
          p.price, p.unit, p.open, p.featured, data[i][9]
        ]]);
        return { ok: true };
      }
    }
    return { ok: false, msg: '找不到課程' };
  } else {
    // 新增
    const rows = sh.getLastRow();
    const newId = 'C' + String(rows).padStart(3,'0');
    sh.appendRow([newId, p.name, p.type, p.desc, p.icon, p.price, p.unit, p.open, p.featured, now]);
    return { ok: true, id: newId };
  }
}

// 後台：刪除課程
function _adminDeleteCourse(p) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET.COURSES);
  const data = sh.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === p.id) { sh.deleteRow(i+1); return { ok: true }; }
  }
  return { ok: false, msg: '找不到課程' };
}

// 後台：核對付款
function _adminVerifyPayment(p) {
  const ss  = SpreadsheetApp.getActiveSpreadsheet();
  const pSh = ss.getSheetByName(SHEET.PAYMENTS);
  const oSh = ss.getSheetByName(SHEET.ORDERS);
  const now = _now();

  const pData = pSh.getDataRange().getValues();
  for (let i = 1; i < pData.length; i++) {
    if (pData[i][0] === p.payId) {
      pSh.getRange(i+1, 8).setValue(p.status);   // 核對狀態
      pSh.getRange(i+1, 9).setValue(now);          // 核對時間
      pSh.getRange(i+1, 10).setValue(p.note||''); // 核對備註
      // 同步更新訂單狀態
      const orderId = pData[i][1];
      const oData   = oSh.getDataRange().getValues();
      for (let j = 1; j < oData.length; j++) {
        if (oData[j][0] === orderId) {
          oSh.getRange(j+1, 10).setValue(p.status === '已核對' ? '已付款' : '待對帳');
          oSh.getRange(j+1, 11).setValue(now);
          break;
        }
      }
      return { ok: true };
    }
  }
  return { ok: false, msg: '找不到付款記錄' };
}

// 後台：手動更新訂單
function _adminUpdateOrder(p) {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  const oSh  = ss.getSheetByName(SHEET.ORDERS);
  const data = oSh.getDataRange().getValues();
  const now  = _now();
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === p.orderId) {
      if (p.status) oSh.getRange(i+1, 10).setValue(p.status);
      if (p.note !== undefined) oSh.getRange(i+1, 9).setValue(p.note);
      oSh.getRange(i+1, 11).setValue(now);
      return { ok: true };
    }
  }
  return { ok: false, msg: '找不到訂單' };
}

// 後台：Dashboard 統計
function _adminDashboard() {
  const orders   = _readSheet(SHEET.ORDERS);
  const payments = _readSheet(SHEET.PAYMENTS);
  const courses  = _readSheet(SHEET.COURSES);

  const thisMonth = new Date();
  const ym = `${thisMonth.getFullYear()}-${String(thisMonth.getMonth()+1).padStart(2,'0')}`;

  const monthOrders = orders.filter(o => String(o['報名時間']).startsWith(ym));
  const paid        = payments.filter(p => p['核對狀態'] === '已核對');
  const paidIds     = new Set(paid.map(p => p['訂單編號']));

  const totalRevenue   = paid.reduce((s,p) => s + Number(p['實付金額']||0), 0);
  const pendingOrders  = orders.filter(o => !paidIds.has(o['訂單編號']));
  const pendingAmount  = pendingOrders.reduce((s,o) => s + Number(o['應付金額']||0), 0);

  // 月趨勢（近6個月）
  const trend = [];
  for (let m = 5; m >= 0; m--) {
    const d   = new Date(); d.setMonth(d.getMonth()-m);
    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
    const mo  = orders.filter(o => String(o['報名時間']).startsWith(key));
    const rev = payments
      .filter(p => {
        const o = orders.find(x => x['訂單編號'] === p['訂單編號']);
        return o && String(o['報名時間']).startsWith(key) && p['核對狀態'] === '已核對';
      })
      .reduce((s,p) => s + Number(p['實付金額']||0), 0);
    trend.push({ month: key, orders: mo.length, revenue: rev });
  }

  // 課程分布
  const byCourse = courses.map(c => ({
    id: c['課程ID'], name: c['課程名稱'],
    count: orders.filter(o => o['課程ID'] === c['課程ID']).length
  }));

  return {
    ok: true,
    data: {
      totalRevenue,
      pendingAmount,
      pendingCount:  pendingOrders.length,
      monthOrders:   monthOrders.length,
      paidCount:     paid.length,
      verifyRate:    orders.length ? Math.round(paidIds.size / orders.length * 100) : 0,
      trend,
      bycourse: bycourse,
    }
  };
}

// ════════════════════════════════════════════════════════════
//  工具函式
// ════════════════════════════════════════════════════════════
function _readSheet(name) {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  const sh   = ss.getSheetByName(name);
  if (!sh || sh.getLastRow() < 2) return [];
  const data = sh.getDataRange().getValues();
  const hdrs = data[0];
  return data.slice(1).map(row =>
    Object.fromEntries(hdrs.map((h,i) => [h, row[i]]))
  );
}

function _now()  { return Utilities.formatDate(new Date(),'Asia/Taipei','yyyy-MM-dd HH:mm:ss'); }
function _fmt(d) { return Utilities.formatDate(d,'Asia/Taipei','yyyy-MM-dd HH:mm:ss'); }
function _fmtDisplay(v) {
  if (v instanceof Date) return Utilities.formatDate(v,'Asia/Taipei','yyyy/MM/dd HH:mm');
  return String(v).replace('T',' ').slice(0,16);
}
function _cleanPhone(p) { return p.replace(/\D/g,''); }
function _normalizePhone(p) {
  const c = p.replace(/\D/g,'');
  return c.startsWith('0') ? c.slice(1) : c;
}
function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
