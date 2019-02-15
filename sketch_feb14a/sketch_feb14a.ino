#define TRIG 7
#define PULSE 6

const unsigned long TIMEOUT = 100 * 58;

unsigned long t0 = millis();
float duration = 0;

void setup() {

  pinMode(TRIG, OUTPUT);
  pinMode(PULSE, INPUT);

  Serial.begin(9600);

}

void loop() {

  if (millis() - t0 > 100) {

      t0 = millis();
      
      digitalWrite(TRIG, LOW);
      delayMicroseconds(5);
      digitalWrite(TRIG, HIGH);
      delayMicroseconds(10);
      digitalWrite(TRIG, LOW);
    
      duration = pulseIn(PULSE, HIGH, TIMEOUT) / 58.0;
    
      Serial.println(duration);

  }


  
}
