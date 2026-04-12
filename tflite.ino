#include <TensorFlowLite.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model.h"

constexpr int kTensorArenaSize = 30 * 1024;
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

tflite::AllOpsResolver resolver;
tflite::MicroErrorReporter micro_error_reporter;
tflite::ErrorReporter* error_reporter = &micro_error_reporter;

const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input  = nullptr;
TfLiteTensor* output = nullptr;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  model = tflite::GetModel(gait_model_tflite);  // ← replace model_tflite with your array name
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Schema version mismatch!");
    return;
  }

  static tflite::MicroInterpreter static_interpreter(
    model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
  interpreter = &static_interpreter;

  TfLiteStatus alloc_status = interpreter->AllocateTensors();
  if (alloc_status != kTfLiteOk) {
    Serial.println("AllocateTensors FAILED");
    return;
  }

  Serial.println("AllocateTensors OK!");
  input  = interpreter->input(0);
  output = interpreter->output(0);

  Serial.print("Input dims: ");
  for (int i = 0; i < input->dims->size; i++) {
    Serial.print(input->dims->data[i]);
    Serial.print(" ");
  }
  Serial.println();
  Serial.print("Input type: "); Serial.println(input->type);
}

void loop() {
  if (interpreter == nullptr || input == nullptr) {
    Serial.println("Not initialized");
    delay(1000);
    return;
  }

  for (int i = 0; i < input->dims->data[1]; i++) {
    input->data.f[i] = 0.0f;
  }

  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("Invoke FAILED");
    return;
  }

  for (int i = 0; i < output->dims->data[1]; i++) {
    Serial.print("Output[");
    Serial.print(i);
    Serial.print("]: ");
    Serial.println(output->data.f[i], 4);
  }
  delay(500);
}
