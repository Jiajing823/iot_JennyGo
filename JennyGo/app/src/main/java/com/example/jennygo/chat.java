package com.example.jennygo;

import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;


import com.google.android.material.floatingactionbutton.FloatingActionButton;

import org.json.JSONObject;
import org.w3c.dom.Text;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class chat extends AppCompatActivity {
    private final int REQ_CODE = 100;
    private ListView msgListView;
    private FloatingActionButton send;
    private MsgAdapter adapter;
    private List<Msg> msgList = new ArrayList<Msg>();
    TextView words;
//    TextView info;
    TextView text1;
    TextView text2;
    public String received;
    TextToSpeech t1;
    public int is_reply;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        ActionBar actionBar = getSupportActionBar();
        actionBar.hide();

//        setContentView(R.layout.activity_main);
        initMsgs();
        sendPost("send", "http://104.196.199.145:5000/turtle/status/capture");
        text1 = findViewById(R.id.pers);
        text2 = findViewById(R.id.mood);
        adapter = new MsgAdapter(chat.this, R.layout.msg_item, msgList);
        send =  findViewById(R.id.send);
        msgListView = (ListView) findViewById(R.id.msg_list_view);
        msgListView.setAdapter(adapter);
        t1 = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status != TextToSpeech.ERROR) {
                    t1.setLanguage(Locale.US);
                    t1.speak("Hello, how are you?", TextToSpeech.QUEUE_FLUSH, null, null);
                }
            }
        });
        send.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                promptSpeechInput();

            }
        });
    }
    private void promptSpeechInput() {

        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, "en-US");

        try {
            startActivityForResult(intent, REQ_CODE);
//
        } catch (ActivityNotFoundException a) {
            Toast t = Toast.makeText(getApplicationContext(),"Opps! Your device doesn't support Speech to Text", Toast.LENGTH_SHORT);
            t.show();
        }
    }
    private void initMsgs() {
        Msg msg1 = new Msg("Hello, how are you?", Msg.TYPE_RECEIVED);
        msgList.add(msg1);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case REQ_CODE: {
                if (resultCode == RESULT_OK && null != data) {

                    ArrayList<String> result = data
                            .getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
//                    txtInput.setText(result.get(0));
                    String content = result.get(0);
//                if(!"".equals(content)) {
                    if (content != null){
                        Msg msg = new Msg(content, Msg.TYPE_SEND);
                        msgList.add(msg);
                        adapter.notifyDataSetChanged();
                        msgListView.setSelection(msgList.size());
                        Log.d("print",content);
                        httpPost(content);
                    }

                }
                break;
            }

        }
    }

    private void httpPost(final String s) {
        //开子线程网络请求
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL url = new URL("http://104.196.199.145:5000/turtle/post/result");
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
                    is_reply = 0;
                    DataOutputStream outputStream = new DataOutputStream(connection.getOutputStream());
                    String content = s;
                    outputStream.writeBytes(content);
                    outputStream.flush();
                    outputStream.close();

                    if (connection.getResponseCode() == 200) {
                        InputStream is = connection.getInputStream();
                        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
                        StringBuffer stringBuffer = new StringBuffer();//使用StringBuffer来存储所有信息
                        String readLine = "";//使用readLine方法来存储整行信息
                        while ((readLine = reader.readLine()) != null) {
                            stringBuffer.append(readLine);                        }
                        is.close();
                        reader.close();
                        connection.disconnect();
                        Log.d("Message", stringBuffer.toString());
                        is_reply = 1;
                        pronounce(stringBuffer.toString());

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
    private void pronounce(final String response){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                words = findViewById(R.id.left_msg);
//                info = findViewById(R.id.info);
                try {
                    String content = new String(response.getBytes(),"UTF-8");
                    final String ans = content.split(",   ")[0].split(":")[1].split("\"")[1];
                    received = ans;
                    final String cla = content.split(",   ")[1].split(":")[1].split("\"")[1];
                    String mood = content.split(",   ")[2].split(":")[1].split("\"")[1];
                    String pers = content.split(",   ")[3].split(":")[1].split("\"")[1];

                    String cla_before = cla;
//                    if (cla_before == cla) {info.setText(" ");}
//                    else {info.setText(cla);}
                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            words.setText(ans);

                            Toast.makeText(getApplicationContext(), ans,Toast.LENGTH_SHORT).show();
                        }},1000);
                    words.addTextChangedListener(new TextWatcher() {
                        public void afterTextChanged(Editable s) {
                            final String toSpeak = ans;

                            Log.d("answer",ans);
                            if (is_reply == 1){
                            t1 = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
                                @Override
                                public void onInit(int status) {
                                    if (status != TextToSpeech.ERROR) {

                                            t1.setLanguage(Locale.US);
                                            t1.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null, null);
                                            is_reply = 0;
                                    }
                                }
                            });
                            }
                        }

                        public void beforeTextChanged(CharSequence s, int start,
                                                      int count, int after) {
                        }

                        public void onTextChanged(CharSequence s, int start,
                                                  int before, int count) {

                        }
                    });
                    Msg msg_ = new Msg(received, Msg.TYPE_RECEIVED);
                    msgList.add(msg_);
                    adapter.notifyDataSetChanged();
                    msgListView.setSelection(msgList.size());
                    Log.d("pers",pers);
                    Log.d("mood",mood);
                    text1.setText("Personality: " + pers );
                    text2.setText("Mood: " + mood);
                } catch (UnsupportedEncodingException e) {
                    e.printStackTrace();
                }
            }
        });
    }

}
