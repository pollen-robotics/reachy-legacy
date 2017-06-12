#include <math.h>
#include <stdio.h>
#include <unistd.h>

#include "zhelpers.h"


int main() {
  void *context = zmq_ctx_new();
  void *client = zmq_socket(context, ZMQ_REQ);

  // Connects to the robot server.
  zmq_connect(client, "tcp://reachy.local:9898");
  printf("Connecting to reachy...\n");

  // Read the position of one motor: "shoulder_roll".
  char *pos_cmd = "{\"robot\": {\"get_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"present_position\"}}}";
  s_send(client, pos_cmd);
  printf("Shoulder roll current position: %s\n", s_recv(client));

  // Read the speed of one motor: "shoulder_roll".
  char *speed_cmd = "{\"robot\": {\"get_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"present_speed\"}}}";
  s_send(client, speed_cmd);
  printf("Shoulder roll current speed: %s\n", s_recv(client));

  // Set the "shoulder_roll" motor to stiff (not compliant).
  char *compliant_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"compliant\", \"value\": \"false\"}}}";
  s_send(client, compliant_cmd);
  printf("Shoulder roll is now stiff (error: %s)\n", s_recv(client));

  // Set the "shoulder_roll" motor goal maximum speed to 50rpm.
  char *max_speed_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"moving_speed\", \"value\": \"50\"}}}";
  s_send(client, max_speed_cmd);
  printf("Shoulder roll max speed is now moving 50 (error: %s)\n", s_recv(client));

  // Set the "shoulder_roll" motor goal position to 45.
  char *move_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"goal_position\", \"value\": \"45\"}}}";
  s_send(client, move_cmd);
  printf("Shoulder roll is now moving to position 45 (error: %s)\n", s_recv(client));

  sleep(3);

  // Set the "shoulder_roll" motor goal position back to 0.
  char *back_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"shoulder_roll\", \"register\": \"goal_position\", \"value\": \"0\"}}}";
  s_send(client, back_cmd);
  printf("Shoulder roll is now moving to position 0 (error: %s)\n", s_recv(client));

  sleep(3);

  // Make the "arm_yaw" motor follows a sinusoid for 5s.
  // First we set it to stiff mode.
  char *stiff_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"arm_yaw\", \"register\": \"compliant\", \"value\": \"false\"}}}";
  s_send(client, stiff_cmd);
  s_recv(client);

  float freq = 0.5;
  float amp = 30;
  int period = 20 * 1000; // we update position every 20ms
  int duration = 5;
  int steps = 50 * duration;

  char cmd[256];
  char *sin_cmd = "{\"robot\": {\"set_register_value\": {\"motor\": \"arm_yaw\", \"register\": \"goal_position\", \"value\": \"%g\"}}}";
  char *get_cmd = "{\"robot\": {\"get_register_value\": {\"motor\": \"arm_yaw\", \"register\": \"present_position\"}}}";

  // Then we affect new pos every 20ms.
  for (float t=0; t < duration; t += 0.02) {
    float pos = amp * sin(2 * M_PI * freq * t);

    snprintf(cmd, sizeof(cmd), sin_cmd, pos);
    s_send(client, cmd);
    s_recv(client);

    s_send(client, get_cmd);
    printf("Current pos %s Goal pos %g\n", s_recv(client), pos);

    usleep(period);
  }

  return 0;
}
