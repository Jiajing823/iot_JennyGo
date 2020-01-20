package com.example.jennygo;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import android.content.Context;

import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.Button;
import android.widget.EditText;
import java.net.URL;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Timer;
import java.util.TimerTask;
import java.io.DataOutputStream;
import java.net.MalformedURLException;
import android.os.Handler;
import java.util.HashMap;

public class MainActivity extends AppCompatActivity {

    private final int REQ_CODE = 100;
    Animation rotateAnimation;
    Animation alphaAnimation;
    Animation lotusAnimation;
    TextView text;
    TextView f_text1;
    TextView f_text2;
    TextView text1;
    TextView text2;
    TextView words;
    ImageView bkgd;
    public boolean is_hot = false;
    public boolean is_wet = false;
    ImageView lt;
    ImageButton fab;
    Timer t;
    TextToSpeech t1;
    //    EditText ed1;
    Button b1;
    public String light = "0";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        rotateAnimation = AnimationUtils.loadAnimation(this, R.anim.rotate);
        alphaAnimation = AnimationUtils.loadAnimation(this, R.anim.alpha);
        lotusAnimation = AnimationUtils.loadAnimation(this, R.anim.lotus);
        Toolbar toolbar = findViewById(R.id.toolbar);
//        txtInput = (TextView) findViewById(R.id.txtInput);
        setSupportActionBar(toolbar);

        fab = findViewById(R.id.fab);
        ImageView tv = findViewById(R.id.tv);
        tv.startAnimation(rotateAnimation);
        ImageButton tvbk = findViewById(R.id.tvbk);
        tvbk.startAnimation(alphaAnimation);
        lt = findViewById(R.id.lt);
        bkgd = findViewById(R.id.bkgd);
        lt.startAnimation(lotusAnimation);

//        t1=new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
//            @Override
//            public void onInit(int status) {
//                if(status != TextToSpeech.ERROR) {
//                    t1.setLanguage(Locale.US); }
//            }
//        });

        words=(TextView)findViewById(R.id.word);
        words.setText(light);
        f_text1 = (TextView)findViewById(R.id.fake_temp);
        f_text2 = (TextView)findViewById(R.id.fake_humid);
        b1=(Button)findViewById(R.id.button);
        words.addTextChangedListener(new TextWatcher() {
            public void afterTextChanged(Editable s) {
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                if(light.contains("0")){
                    Log.d("Light0", light);
                    lt.setImageDrawable(getResources().getDrawable(R.drawable.lotus,null));
                    bkgd.setImageDrawable(getResources().getDrawable(R.drawable.background,null));
                }
                else {
                    Log.d("Light1", light);
                    lt.setImageDrawable(getResources().getDrawable(R.drawable.lotus_dark, null));
                    bkgd.setImageDrawable(getResources().getDrawable(R.drawable.background_dark, null));
                }
            }
        });

        f_text1.addTextChangedListener(new TextWatcher() {
            public void afterTextChanged(Editable s) {
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                if(is_hot){
                    Log.d("Hot0", "true");
                    text1.setTextColor(text1.getTextColors().withAlpha(255));
                }
                else {
                    Log.d("Hot1", "false");
                    text1.setTextColor(text1.getTextColors().withAlpha(0));
                }
            }
        });
        f_text2.addTextChangedListener(new TextWatcher() {
            public void afterTextChanged(Editable s) {
            }

            public void beforeTextChanged(CharSequence s, int start,
                                          int count, int after) {
            }

            public void onTextChanged(CharSequence s, int start,
                                      int before, int count) {
                if(is_wet){
                    Log.d("Humid0", "true");
                    text2.setTextColor(text2.getTextColors().withAlpha(255));
                }
                else {
                    Log.d("Humid1", "false");
                    text2.setTextColor(text2.getTextColors().withAlpha(0));
                }
            }
        });


        fab.setOnClickListener(new View.OnClickListener() {
                                   @Override
                                   public void onClick(View view) {
                                       DownloadImageFromPath();
//                                       Intent i = new Intent(MainActivity.this , Snapshot.class);
//                                       startActivity(i);
//                Intent i = new Intent(MainActivity.this , chat.class);
//                startActivity(i);
                                   }
                               });

        t = new Timer();
        t.schedule(new TimerTask() {
            public void run() {
                httpGet();
            }
        }, 0, 30000);
        text = findViewById(R.id.environment);
        text1 = findViewById(R.id.temp);
        text2 = findViewById(R.id.humid);
        text1.setText("Too hot!");
        text2.setText("Too dry!");
        sendPost("send", "http://104.196.199.145:5000/turtle/status/monitor");
        sendPost("send", "http://104.196.199.145:5000/turtle/status/snapshot");

//        words.addTextChangedListener(new TextWatcher() {
//            public void afterTextChanged(Editable s) {
//
//            }
//            public void beforeTextChanged(CharSequence s, int start,
//                                          int count, int after) { }
//            public void onTextChanged(CharSequence s, int start,
//                                      int before, int count) {
////                String toSpeak = ed1.getText().toString();
//                String toSpeak = "I can hear you";
//                Toast.makeText(getApplicationContext(), toSpeak,Toast.LENGTH_SHORT).show();
//                t1.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null);
//            }
        b1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(MainActivity.this , chat.class);
                startActivity(i);
//                String toSpeak = "I can hear you";
//                Toast.makeText(getApplicationContext(), toSpeak,Toast.LENGTH_SHORT).show();
//                t1.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null);
            }
        });
//
    }
    public void onResume() {
        super.onResume();
        sendPost("send", "http://104.196.199.145:5000/turtle/status/monitor");
    }
    public void onPause(){
        if(t1 !=null){
            t1.stop();
            t1.shutdown();
        }
        super.onPause();
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }


    private void httpGet() {
        //开子线程网络请求
        new Thread(new Runnable() {
            @Override
            public void run() {
                HttpURLConnection connection=null;
                BufferedReader reader=null;
                String urls="http://104.196.199.145:5000/turtle/get/stats";

                try {
                    URL url=new URL(urls);
                    connection=(HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setReadTimeout(5000);
                    connection.setConnectTimeout(5000);
                    InputStream in=connection.getInputStream();

                    reader = new BufferedReader( new InputStreamReader(in));
                    StringBuilder response =new StringBuilder();
                    String line;
                    while ((line=reader.readLine())!=null){
                        response.append(line);
                    }
                    Log.e("test",response.toString());
                    showResponse(response.toString());
                } catch (IOException e) {
                    e.printStackTrace();
                }finally {
                    if (reader!=null){
                        try {
                            reader.close();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                    if (connection!=null){
                        connection.disconnect();
                    }
                }


            }
        }).start();
    }
    public void DownloadImageFromPath() {

        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    InputStream in = null;
                    Bitmap bmp = null;
                    int responseCode = -1;
                    URL url = new URL("http://104.196.199.145:5000/turtle/get/img/snapshots");
                    HttpURLConnection con = (HttpURLConnection) url.openConnection();
                    con.setDoInput(true);
                    con.connect();
                    responseCode = con.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        //download
                        in = con.getInputStream();
                        bmp = BitmapFactory.decodeStream(in);
                        in.close();
                        showImage(bmp);
                    }
                } catch (Exception ex) {
                    Log.e("Exception", ex.toString());
                }
            }
        }).start();
    }
    private void sendPost(final String s, final String address) {
        //开子线程网络请求
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL(address);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();

                    connection.setDoOutput(true);
                    connection.setDoInput(true);
                    connection.setUseCaches(false);
                    connection.setRequestMethod("POST");
                    connection.setRequestProperty("Accept-Charset", "UTF-8");
                    connection.setRequestProperty("Content-Type", "application/x-www-form-urlenc");
//                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
//                connection.setRequestProperty("Accept", "application/json");
                    connection.connect();

                    DataOutputStream outputStream = new DataOutputStream(connection.getOutputStream());
                    String content = s;
                    outputStream.writeBytes(content);
                    outputStream.flush();
                    outputStream.close();

                    if (connection.getResponseCode() == 200) {
                        connection.disconnect();
                        Log.d("Message", "Connected");

                    } else {                        //打印错误的信息
                        Log.d("Messages", "ERROR ");
                    }
                } catch (MalformedURLException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
    //切换为主线程
    private void showResponse(final String response){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {

                try {
                    String content = new String(response.getBytes(),"UTF-8");
                    Log.d("sensor",content);
                    String humid = content.split(",")[0].split(":")[1];

                    light = content.split(",")[1].split(":")[1];
                    Log.d("light",light);
                    String temp1 = content.split(",")[2].split(":")[1];
                    String temp = temp1.substring(1,3);
                    text.setText(temp+"℃        "+humid+"%");
                    words.setText(light);
                    is_hot = (Integer.valueOf(temp.substring(0,2)) > 30);
                    Log.d("temp",temp.substring(0,2));
                    is_wet = (Integer.valueOf(humid.substring(1,3)) < 20);
                    Log.d("humid",humid.substring(1,3));
                    if(Integer.valueOf(temp.substring(0,2)) > 30){
                        Log.d("shallow", "0");
                        f_text1.setText("0");}
                    else{Log.d("shallow", "1");
                        f_text1.setText("1");}
                    if(Integer.valueOf(humid.substring(1,3))< 20){
                        Log.d("dark", "0");
                        f_text2.setText("0");}
                    else{
                        Log.d("dark", "1");
                        f_text2.setText("1");}

                    //把获取的网页数据赋值给变量response，并设置给TextView控件
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    //切换为主线程
    private void showImage(final Bitmap bmp){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                final ImageButton ib = (ImageButton) findViewById(R.id.img1bk);
                try {
                    ib.setImageBitmap(bmp);
                    ib.setOnClickListener(new View.OnClickListener() {
                        @Override
                        public void onClick(View v) {
                            ib.setImageResource(android.R.color.transparent);
                        }
                    });
                } catch (Exception ex) {
                    Log.e("Exception", ex.toString());}
            }
        });
    }
}
