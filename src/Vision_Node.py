import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import json

from Onboard_Vision import OnboardVision

class VisionPublisherNode(Node):
    def __init__(self):
        super().__init__('uav_vision_node')
        
        self.data_publisher = self.create_publisher(String, '/vision/target_detections', 10)
        self.image_publisher = self.create_publisher(Image, '/vision/video_feed', 10)
        
        self.bridge = CvBridge()
        
        self.get_logger().info("Initializing Onboard Vision...")
        self.vision = OnboardVision(initialModelPath="yolo26n.pt", targetObjects=[])
        self.vision.cameraStart()
        
        self.timer = self.create_timer(1/30.0, self.vision_loop)

    def vision_loop(self):
        detections, frame = self.vision.detection()
        
        if detections:
            for det in detections:
                msg = String()
                msg.data = json.dumps(det)
                self.data_publisher.publish(msg)
                self.get_logger().info(f"Published Target: {msg.data}")
                
        if frame is not None:
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.image_publisher.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)
    node = VisionPublisherNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.vision.cameraStop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()