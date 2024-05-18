package com.haridroid.uavcapstone;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";

    private TextView connectionStatusTextView;
    TextView tempValue,humidValue, gasValue;
    private ListView receivedDataListView;
    private ArrayAdapter<String> receivedDataAdapter;
    private ServerSocket serverSocket;
    private Handler handler = new Handler();
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        connectionStatusTextView = findViewById(R.id.connection_status);
        receivedDataListView = findViewById(R.id.received_data_list);
        tempValue= findViewById(R.id.Temperature_value);
        humidValue= findViewById(R.id.Humidity_value);
        gasValue= findViewById(R.id.Gas_value);



        // Initialize the ArrayAdapter for the ListView
        ArrayList<String> receivedDataList = new ArrayList<>();
        receivedDataAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, receivedDataList);
        receivedDataListView.setAdapter(receivedDataAdapter);

        // Start a background thread to listen for incoming connections
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // Create a server socket
                    serverSocket = new ServerSocket(12345);

                    // Update connection status
                    updateConnectionStatus("Waiting for connections...");

                    // Listen for incoming connections
                    while (true) {
                        Socket socket = serverSocket.accept();
                        // Update connection status
                        updateConnectionStatus("Connected to Client");

                        // Read data from the client
                        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                        String line;
                        while ((line = reader.readLine()) != null) {
                            // Log received data
                            Log.d(TAG, "Received: " + line);
                            // Update the UI with received data
                            updateReceivedData(line);
                            if (line.startsWith("Temperature:")) {
                                updateTemperature(line);
                            } else if (line.startsWith("Humidity:")) {
                                updateHumidity(line);
                            } else if (line.equals("Harmful gases detected!")) {
                                updateAirQuality(line);
                            }
                        }

                        // Close the socket when done
                        socket.close();

                        // Update connection status
                        updateConnectionStatus("Waiting for connections...");
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    private void updateConnectionStatus(final String status) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                connectionStatusTextView.setText(status);
            }
        });
    }

    private void updateReceivedData(final String data) {
        handler.post(new Runnable() {
            @Override
            public void run() {
                receivedDataAdapter.add(data);
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Close the server socket when the activity is destroyed
        try {
            if (serverSocket != null) {
                serverSocket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    // Method to update UI with temperature data
    private void updateTemperature(String data) {
        // Extract temperature value
        String temperature = data.substring(13); // Assuming "Temperature: " is 13 characters long
        // Update UI with temperature value
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                tempValue.setText(temperature);
            }
        });
    }

    // Method to update UI with humidity data
    private void updateHumidity(String data) {
        // Extract humidity value
        String humidity = data.substring(10); // Assuming "Humidity: " is 10 characters long
        // Update UI with humidity value
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                humidValue.setText(humidity);
            }
        });
    }

    // Method to update UI with air quality data
    private void updateAirQuality(String data) {
        // Update UI with air quality data
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                gasValue.setText(data);
            }
        });
    }
}