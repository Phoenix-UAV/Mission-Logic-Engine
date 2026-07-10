import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import json

from GCS_Display import GCSDisplay

class GCSReceiverNode(Node):
    def __init__(self):
        super().__init__('uav_gcs_display_node')
        
        self.bridge = CvBridge()
        
        self.display = GCSDisplay()
        self.display.cameraStart()
        
        self.image_subscriber = self.create_subscription(
            Image,
            '/vision/video_feed',
            self.image_callback,
            10
        )
        
        self.data_subscriber = self.create_subscription(
            String,
            '/vision/target_detections',
            self.data_callback,
            10
        )
        
        self.latest_detections = []
        self.get_logger().info("GCS Display Node Started. Waiting for Jetson feed...")

    def data_callback(self, msg):
        try:
            target_data = json.loads(msg.data)
            self.latest_detections.append(target_data)

        except Exception as e:
            self.get_logger().error(f"Failed to parse data: {e}")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            self.display.detection(frame, self.latest_detections)
            
            self.latest_detections = []
            
        except Exception as e:
            self.get_logger().error(f"Image processing error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = GCSReceiverNode()
    
    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass
    
    finally:
        node.display.cameraStop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()