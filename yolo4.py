#!/usr/bin/env python3
import argparse
import cv2
import time
from oakd_yolo.oakd_yolo import OakdYolo
from akari_client import AkariClient

# ヘッドを2回頷かせる関数
def nod_head(joints, duration=1):
    joints.move_joint_positions(tilt=-0.524)
    time.sleep(duration)
    joints.move_joint_positions(tilt=0.349)
    time.sleep(duration)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        help="Provide model name or model path for inference",
        default="yolov4_tiny_coco_416x416",
        type=str,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Provide config path for inference",
        default="json/yolov4-tiny.json",
        type=str,
    )
    parser.add_argument(
        "-f",
        "--fps",
        help="Camera frame fps. This should be smaller than nn inference fps",
        default=10,
        type=int,
    )
    args = parser.parse_args()

    end = False
    desired_labels = {0, 1}
    confidence_threshold = 0.6

    # Akariロボット初期化
    akari = AkariClient()
    joints = akari.joints
    joints.enable_all_servo()
    joints.set_joint_velocities(pan=5, tilt=5)
    joints.set_servo_enabled(pan=True, tilt=True)
    joints.move_joint_positions(pan=0, tilt=0.32)

    oakd_yolo = OakdYolo(args.config, args.model, args.fps)
    try:
        while not end:
            frame = None
            detections = []
            try:
                frame, detections = oakd_yolo.get_frame()
            except Exception as e:
                print(f"get_frame() error! {e}")
                break

            if frame is not None:
                oakd_yolo.display_frame("AKARI_VIEW", frame, detections)

                # 検出されたラベルが0または1で、かつ信頼度が0.6以上の場合
                for detection in detections:
                    label = detection.label
                    confidence = detection.confidence
                    if label in desired_labels and confidence >= confidence_threshold:
                        print(f"ラベル {label} が信頼度 {confidence} で検出されました。プログラムを停止します。")

                        # ヘッドを2回頷かせる
                        nod_head(joints)
                        nod_head(joints)
                        
                        key = cv2.waitKey(0)
                        if key == ord("q"):
                            end = True
	
                        #break

            key = cv2.waitKey(1)
            if key == ord("q"):
                end = True

    finally:
        # プログラム終了時にヘッドのサーボモーターをオフにする
        joints.disable_all_servo()
        akari.close()
        oakd_yolo.close()

if __name__ == "__main__":
    main()

