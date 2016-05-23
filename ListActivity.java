package com.example.myfirst;

import android.R.color;
import android.app.Activity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.app.ActivityManager;
import android.app.ActivityManager.RunningAppProcessInfo;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import java.util.*;
import java.text.*;
import android.content.pm.*;
import android.graphics.Color;
import android.widget.*;
import android.widget.RelativeLayout.LayoutParams;
import android.app.ApplicationErrorReport.*;
import android.view.*;
import android.graphics.drawable.*;
import android.graphics.pdf.PdfDocument.Page;
import android.net.Uri;
import android.text.*;
import android.text.format.Formatter;
import android.util.Log;
import android.view.View.*;
import android.os.*;
import android.os.Debug;
import android.app.*;
import java.lang.reflect.*;
import java.io.*;

public class ListActivity extends Activity implements TabHost.TabContentFactory {
	private ActivityManager am=null;
	private PackageManager pm=null;
	private static TabHost th=null;
	private static LinearLayout ll1=null;
	private static LinearLayout ll2=null;
	private static LinearLayout ll3=null;
	private static LinearLayout ll4=null;
	private static ListView v1=null;
	private static ListView v2=null;
	private static ListView v3=null;
	private static ListView v4=null;
	private Handler han1;
	private static String av;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
	}
	protected void onStart(){
		super.onStart();
		am=(ActivityManager)getSystemService(Context.ACTIVITY_SERVICE);
		pm=this.getPackageManager();
		v1=getRunningService(this);
		v2=getAllLaunchers(this);
		v3=getRunningProcessInfo(this);
		v4=getInstalledApps(this);
		setContentView(R.layout.activity_main);
		th=(TabHost)findViewById(R.id.tabhost);
		th.setup();
		ActivityManager.MemoryInfo mmi=new ActivityManager.MemoryInfo();
		am.getMemoryInfo(mmi);
		long available=mmi.availMem;
		av=available/1024/1024+"MB";
		setTabHost(this);
		Toast.makeText(this, "ϵͳ��ǰ�����ڴ�Ϊ"+av, 10000).show();
	}
	protected LinearLayout setlayout(String n){
		LinearLayout.LayoutParams pmm=new LinearLayout
				.LayoutParams(LayoutParams.MATCH_PARENT,LayoutParams.MATCH_PARENT);
		ll1=new LinearLayout(this);
		ll1.setId(R.id.ll1);
		ll1.setLayoutParams(pmm);
		ll1.setOrientation(LinearLayout.VERTICAL);
		ll1.setBackgroundColor(Color.GREEN);
		
		ll2=new LinearLayout(this);
		ll2.setId(R.id.ll2);
		ll2.setLayoutParams(pmm);
		ll2.setOrientation(LinearLayout.VERTICAL);
		ll2.setBackgroundColor(Color.GREEN);
		
		ll3=new LinearLayout(this);
		ll3.setId(R.id.ll3);
		ll3.setLayoutParams(pmm);
		ll3.setOrientation(LinearLayout.VERTICAL);
		ll3.setBackgroundColor(Color.GREEN);
		
		ll4=new LinearLayout(this);
		ll4.setId(R.id.ll4);
		ll4.setLayoutParams(pmm);
		ll4.setOrientation(LinearLayout.VERTICAL);
		ll4.setBackgroundColor(Color.GREEN);
		
		if(n=="tab1"){
			ll1.removeAllViews();
			ll1.addView(v1);
			return ll1;
		}
		else if(n=="tab2"){
			ll2.removeAllViews();
			ll2.addView(v2);
		    return ll2;
		}
		else if(n=="tab3"){
			ll3.removeAllViews();
			ll3.addView(v3);
			return ll3;
		}
		else if(n=="tab4"){
			ll4.removeAllViews();
			ll4.addView(v4);
			return ll4;
		}
		return null;
	} 
	private void setTabHost(Context con){


		th.addTab(th.newTabSpec("tab1").setIndicator("����������Ϣ")
				.setContent(this));
		th.addTab(th.newTabSpec("tab2").setIndicator("��Ԥװ����")
				.setContent(this));
		th.addTab(th.newTabSpec("tab3").setIndicator("�����г���")
				.setContent(this));
		th.addTab(th.newTabSpec("tab4").setIndicator("����Ӧ�ó���")
				.setContent(this));
	}
	
	public LinearLayout createTabContent(String tag){
		final LinearLayout fily=setlayout(tag);
		return fily;
	}
	//�ؼ����룻setcontent();
	protected ListView getRunningService(Context con){
		int flag=1;
		List<String> al=new ArrayList<String>();
		List<Drawable> dw=new ArrayList<Drawable>();
		List<String> names=new ArrayList<String>();
		List<ActivityManager.RunningServiceInfo> services=am.getRunningServices(200);
		Iterator<ActivityManager.RunningServiceInfo> it;
		for(it=services.iterator();it.hasNext();){
			ActivityManager.RunningServiceInfo info=it.next();
			al.add("�������ƣ�\n"+info.service.toString()+"\n"+
					"���ʼʱ�䣺"+formatData(info.activeSince)+"\n"+
					"Client������"+info.clientCount+"\n"+
					"�����ʱ�䣺"+formatData(info.lastActivityTime)+"\n"+
					"����"+info.process+"\n");
			names.add(info.service.toString());
		}
		
        ListView sc=setMyView(al,flag,names);
		return sc;
	}
	protected ListView getAllLaunchers(Context con){
		int flag=2;
		List<String> al=new ArrayList<String>();
		List<Drawable> dw=new ArrayList<Drawable>();
		List<String> names=new ArrayList<String>();
		
		Intent it=new Intent(Intent.ACTION_MAIN);
		it.addCategory(Intent.CATEGORY_LAUNCHER);
		List<ResolveInfo> ra=pm.queryIntentActivities(it, 0);
		PackageStats ps=null;
		Formatter fm=new Formatter();
		//����manifest�е�<intent-filter>��
		for(int i=0;i<ra.size();i++){
			String packageName=ra.get(i).activityInfo.packageName;
			try{
			dw.add(ra.get(i).activityInfo.loadIcon(pm));
			names.add(packageName);
			}catch(Exception ex){
				ex.printStackTrace();
			}
			ps=new PackageStats(packageName);
			al.add("Ӧ������:\n"+ra.get(i).loadLabel(pm)+"\n"+
			"�����С:"+Formatter.formatFileSize(this,ps.cacheSize)+"\n"+
			"���ݴ�С:"+Formatter.formatFileSize(this,ps.dataSize)+"\n"+
			"Ӧ�ó����С:"+Formatter.formatFileSize(this,ps.codeSize));
		}
		
		ListView sc=setMyView(al,flag,dw,names);
		return sc;
	}
	protected ListView getInstalledApps(Context con){
		int flag=4;
		List<String> al=new ArrayList<String>();
		List<ApplicationInfo> pg=pm.getInstalledApplications(0);
		List<Drawable> dw=new ArrayList<Drawable>();
		List<String> names=new ArrayList<String>();
		
		for(int i=0;i<pg.size();i++){
			dw.add(pm.getApplicationIcon(pg.get(i))); 
			al.add("Ӧ�ó������ƣ�\n"+pg.get(i).loadLabel(pm)+"\n"
					+"Ӧ�ó��������: \n"+pg.get(i).packageName+"\n"
					+"Դ�ļ�������: \n"+pg.get(i).sourceDir+"\n");
			names.add(pg.get(i).processName);
		}
		
		ListView sc=setMyView(al,flag,dw,names);
		return sc;
	}

	protected ListView getRunningProcessInfo(Context con){
		int a=3;
		List<String> al=new ArrayList<String>(); 
		List<RunningAppProcessInfo> rp=am.getRunningAppProcesses();
		List<String> names=new ArrayList<String>();
		int []pids=new int[rp.size()];
		
		for(int i=0;i<rp.size();i++){
			pids[i]=(rp.get(i).pid);
		}
		android.os.Debug.MemoryInfo[] memo=am.getProcessMemoryInfo(pids);
		
		for(int i=0;i<rp.size();i++){
			String runningprocessName=rp.get(i).processName;
			String[] runningpackage=rp.get(i).pkgList;
			if(runningprocessName.equals("system")||
					runningprocessName.equals("android.process.media")||
					runningprocessName.equals("android.process.acore")||
					runningprocessName.equals("com.android.systemui")||
					runningprocessName.equals("com.android.phone")||
					runningprocessName.equals("com.example.myfirst")){
			        continue;
			}
			else{
				al.add("�������н�������\n"+runningprocessName+" \n"+
					       "ռ���ڴ棺"+memo[i].dalvikPrivateDirty+"KB\n"+
	                        "����Ӧ�ó�������\n"+runningapk(runningpackage));
			}
			for(int index=0;index<runningpackage.length;index++){
				names.add(runningprocessName);
			}
		}
		
		ListView sc=setMyView(al,a,names);
		return sc;
	}
	public StringBuilder runningapk(String[] names){
		StringBuilder pkgnames=new StringBuilder();
		for(int j=0;j<names.length;j++){
		    pkgnames.append(names[j]+"\n");
		}
		return pkgnames;
	}
	
	public void uninstallapp(String packagename){
		Uri ur=Uri.fromParts("package", packagename, null);
		Intent it=new Intent(Intent.ACTION_DELETE,ur); 
		if(it!=null){
			th.removeAllViews();
			this.startActivity(it);
		}
	}

	private static String formatData(long data){
		SimpleDateFormat format=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		Date time=new Date(data);
		return format.format(time);
	}
	private ListView setMyView(List<String> Serinfo,int a,List<String> names){
		ListView lv=new ListView(this);
		MyAdapter myadapter=new MyAdapter(Serinfo,a,null,this,names);
		lv.setAdapter(myadapter);
		return lv;
	}
	private ListView setMyView(List<String> Serinfo,int a,List<Drawable> draw,List<String> names){
		ListView lv=new ListView(this);
		MyAdapter myadapter=new MyAdapter(Serinfo,a,draw,this,names);
		lv.setAdapter(myadapter);
		return lv;
	}
	/*private void Killmyprocesses(String processname){
		//����;ɱ�����̵���һ�ַ�����
		try{
			Method fsp=am.getClass().getDeclaredMethod("forceStopPackage", String.class);
		       fsp.setAccessible(true);
		       fsp.invoke(am, processname);
		}catch(Exception ex){
			ex.printStackTrace();
		}
	}*/
	private void CleanMydata(String packagename){
		File fl=new File("/Android/data/"+ packagename + "/cache");//Ѱ���ļ��У�
		if (fl != null && fl.exists() && fl.isDirectory()) {
            for (File item : fl.listFiles()) {
                item.delete();
                Toast.makeText(this, "����ɹ�", 1000).show();
            }
        }
		else{
			Toast.makeText(this, "��������", 1000).show();
		}
	}
	class MyAdapter extends BaseAdapter{//�Զ�����������
		private List<String> lob;
		private List<Drawable> draw;
		private List<String> name;
		private int flags;
		public MyAdapter(List<String> lob,int a,List<Drawable> draw,Context con,List<String> name){
			this.lob=lob;
			this.flags=a;
			this.draw=draw;
			this.name=name;
		}
		public int getCount(){
			return lob.size();
		}
		public Object getItem(int pos){
			return lob.get(pos);
		}
		public long getItemId(int pos){
			return pos;
		}
		public View getView(int pos,View conv,ViewGroup vg){
			if(flags==3){
			       LinearLayout framel=new LinearLayout(ListActivity.this);
			       TableRow tr=new TableRow(ListActivity.this);
			       TextView txt=new TextView(ListActivity.this);
			       txt.setText(lob.get(pos).toString());
			       txt.setTextColor(Color.BLACK);
			       Button bu1=new Button(ListActivity.this);
			       bu1.setText("ǿ�ƹرս���");
			       bu1.setTextSize(10);
			       bu1.getBackground().setAlpha(500);//����͸���ȣ�
			       final int k=pos;
			       final LinearLayout fr=framel;
			       final ListView lvv=v3;
			       bu1.setOnClickListener(new OnClickListener(){
			    	   public void onClick(View v){
			    		   try{
			    			   am.killBackgroundProcesses(name.get(k)); 
			    		   }
			    		   catch(Exception e){
			    			   e.printStackTrace();
			    		   }
			    		   //ҳ��ˢ�£�
			    		   new Thread(new CloseProcess()).start();;
		    			   han1=new Handler(){
		    				   public void handleMessage(Message msg){
		    					   super.handleMessage(msg);
		    					   switch(msg.what){
		    					   case 0:
		    						   System.out.println(name.get(k)); 
		    						   lvv.invalidate();//��������߳��У�
		    						   break;
		    					   default:
		    						   break;
		    					   }
		    				   }
		    			   }; 
			    	   }
			       });
			       framel.addView(txt,450,200);
			       tr.addView(bu1,180,120);
			       framel.addView(tr);
			       return framel;
			}
			else if(flags==2){
				   LinearLayout framel=new LinearLayout(ListActivity.this);
			       TextView txt=new TextView(ListActivity.this);
			       TableRow tr=new TableRow(ListActivity.this);
			       TableRow smalltr1=new TableRow(ListActivity.this);
			       TableRow smalltr2=new TableRow(ListActivity.this);
			       txt.setText(lob.get(pos).toString());
			       txt.setTextColor(Color.BLACK);
			       draw.get(pos).setBounds(0,0, 100, 100);
			       txt.setCompoundDrawables(draw.get(pos),null,null,null);
			       Button bu1=new Button(ListActivity.this);
			       Button bu2=new Button(ListActivity.this);
			       bu1.setText("ж�س���");
			       bu1.setTextSize(15);
			       bu1.getBackground().setAlpha(200);//����͸���ȣ�
			       bu2.setText("������");
			       bu2.setTextSize(15);
			       bu2.getBackground().setAlpha(200);
			       final int i=pos;
			       final LinearLayout tl=framel;
			       bu1.setOnClickListener(new OnClickListener(){
			    	   public void onClick(View v){
			    		   AlertDialog ad=new AlertDialog.Builder(ListActivity.this).create();
			    		   ad.setMessage("�Ƿ�ж�س���");
			    		   ad.setButton(DialogInterface.BUTTON_NEGATIVE,"ȡ��",new AlertDialog.OnClickListener(){
			    			   public void onClick(DialogInterface di,int which){
			    				   Toast.makeText(ListActivity.this, "��ȡ��", 1000).show();
			    			   }
			    		   });
			    		   ad.setButton(DialogInterface.BUTTON_POSITIVE,"ȷ��",new AlertDialog.OnClickListener(){
			    			   public void onClick(DialogInterface di,int which){
			    				   uninstallapp(name.get(i));
			    				   Toast.makeText(ListActivity.this, "ж��...", 1000).show();
			    			   }
			    		   });
			    		   ad.show();
			    	   }
			       });
			       bu2.setOnClickListener(new OnClickListener(){
			    	   public void onClick(View v){
			    		   try{
			    			   CleanMydata(name.get(i));
			    		   }catch(Exception ex){
			    			   ex.printStackTrace();
			    		   }
			    	   }
			       });
			       framel.addView(txt,380,175);
			       smalltr1.addView(bu1,120,175);
			       smalltr2.addView(bu2,120,175);
			       tr.addView(smalltr1);
			       tr.addView(smalltr2);
			       framel.addView(tr);
			       return framel;
			}
			else if(flags==1){
				   LinearLayout framel=new LinearLayout(ListActivity.this);
			       TextView txt=new TextView(ListActivity.this);
			       txt.setText(lob.get(pos).toString());
			       txt.setTextColor(Color.BLACK);
			       framel.addView(txt);
			       return framel;
			}
			else if(flags==4){
				   LinearLayout framel=new LinearLayout(ListActivity.this);
			       TextView txt=new TextView(ListActivity.this);
			       txt.setText(lob.get(pos).toString());
			       txt.setTextColor(Color.BLACK);
			       draw.get(pos).setBounds(0,0, 100, 100);
			       txt.setCompoundDrawables(draw.get(pos),null,null,null);
			       framel.addView(txt);
			       return framel;
			}
			return null;
		}
	}
	class CloseProcess implements Runnable{
		public void run(){
			try{
				Message msg=new Message();
				int CLOSE_PROCESS=0;
				msg.what=CLOSE_PROCESS;
				ListActivity.this.han1.sendMessage(msg);
			}
			catch(Exception e){
			    e.printStackTrace();
			}
		}
	}
}
	
