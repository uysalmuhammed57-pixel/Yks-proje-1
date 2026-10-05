import os
d="android/app/src/main/java/com/yks/sayac/"
os.makedirs(d,exist_ok=True)
F={}
F["MainActivity.java"]=r"""package com.yks.sayac;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
public class MainActivity extends BridgeActivity {
  @Override public void onCreate(Bundle b){ registerPlugin(StopwatchPlugin.class); super.onCreate(b); }
}
"""
F["StopwatchPlugin.java"]=r"""package com.yks.sayac;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
@CapacitorPlugin(name = "Stopwatch")
public class StopwatchPlugin extends Plugin {
  private void done(PluginCall c){
    long[] s = Sw.state(getContext());
    JSObject o = new JSObject(); o.put("acc", s[0]); o.put("start", s[1]); c.resolve(o);
  }
  @PluginMethod public void getState(PluginCall c){ done(c); }
  @PluginMethod public void toggle(PluginCall c){ Sw.toggle(getContext()); done(c); }
  @PluginMethod public void reset(PluginCall c){ Sw.reset(getContext()); done(c); }
}
"""
F["SwReceiver.java"]=r"""package com.yks.sayac;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
public class SwReceiver extends BroadcastReceiver {
  @Override public void onReceive(Context c, Intent i){ Sw.toggle(c); }
}
"""
F["Sw.java"]=r"""package com.yks.sayac;
import android.app.*;
import android.content.*;
import android.os.Build;
public class Sw {
  static SharedPreferences p(Context c){ return c.getSharedPreferences("sw", 0); }
  public static long[] state(Context c){ SharedPreferences p = p(c); return new long[]{ p.getLong("acc",0), p.getLong("start",0) }; }
  static String fmt(long ms){ long t = ms/1000; return (t/3600) + ":" + String.format("%02d:%02d", t%3600/60, t%60); }
  public static void toggle(Context c){
    long[] s = state(c); long now = System.currentTimeMillis();
    if (s[1] > 0) p(c).edit().putLong("acc", s[0] + now - s[1]).putLong("start", 0).apply();
    else p(c).edit().putLong("start", now).apply();
    show(c);
  }
  public static void reset(Context c){
    p(c).edit().putLong("acc",0).putLong("start",0).apply();
    ((NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE)).cancel(7);
  }
  static void show(Context c){
    NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
    if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(new NotificationChannel("sw", "Kronometre", NotificationManager.IMPORTANCE_LOW));
    long[] s = state(c); boolean run = s[1] > 0;
    int fl = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
    PendingIntent act = PendingIntent.getBroadcast(c, 1, new Intent(c, SwReceiver.class), fl);
    PendingIntent open = PendingIntent.getActivity(c, 2, new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), fl);
    Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, "sw") : new Notification.Builder(c);
    b.setSmallIcon(android.R.drawable.ic_menu_recent_history).setContentTitle("Çalışma kronometresi")
     .setOngoing(true).setOnlyAlertOnce(true).setContentIntent(open)
     .addAction(0, run ? "Duraklat" : "Devam et", act);
    if (run) b.setContentText("Çalışıyor").setUsesChronometer(true).setShowWhen(true).setWhen(s[1] - s[0]);
    else b.setContentText("Duraklatıldı: " + fmt(s[0])).setShowWhen(false);
    nm.notify(7, b.build());
  }
}
"""
for n,t in F.items(): open(d+n,"w",encoding="utf-8").write(t)
m="android/app/src/main/AndroidManifest.xml"
t=open(m,encoding="utf-8").read()
t=t.replace("</application>",'<receiver android:name=".SwReceiver" android:exported="false"/></application>')
t=t.replace("<application",'<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/><application',1)
open(m,"w",encoding="utf-8").write(t)
print("patched")
