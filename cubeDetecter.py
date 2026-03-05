import cv2
import numpy as np

def get_adaptive_canny(gray_img):
    """Analise the image and modifie Canny for best results."""
    average_bright = np.mean(gray_img)
    
    # If the average is high (>170), the cube or the background light
    if average_bright > 160:
        return 10, 60
    # Medium
    elif average_bright > 90:
        return 30, 80 
    # Dark
    else:
        return 50, 150
    
def get_grid_points(square_contour):
    # For cases like a white cube with white squares
    
    x, y, w, h = cv2.boundingRect(square_contour)
    
    # Divide the bounding box into a 3x3 grid
    step_x = w // 3
    step_y = h // 3
    
    grid_centers = []
    for row in range(3):
        for col in range(3):
            # Then calculate each center
            cx = x + (col * step_x) + (step_x // 2)
            cy = y + (row * step_y) + (step_y // 2)
            grid_centers.append((cx, cy))
            
    return grid_centers

def sort_centers(centers):
    #Order the 9 points from top-left to bottom-right.
    # First by Y
    centers = sorted(centers, key=lambda p: p[1])
    # Then each line of three by X
    row1 = sorted(centers[0:3], key=lambda p: p[0])
    row2 = sorted(centers[3:6], key=lambda p: p[0])
    row3 = sorted(centers[6:9], key=lambda p: p[0])
    return row1 + row2 + row3

def get_color_name(h, s, v):
    """Simple example of classification."""
    if v < 50: return "Black"
    if s < 40: return "White"
    # valores aproximados de testes
    if h < 10 or h > 160: return "Red"
    if 10 < h < 25: return "Orange"
    if 25 < h < 35: return "Yellow"
    if 35 < h < 85: return "Green"
    if 85 < h < 130: return "Blue"
    return "Indefined"

def get_average_hsv(img_hsv, cx, cy, size=10):
    """Extracts the median color from a central square."""
    h_img, w_img = img_hsv.shape[:2]
    # Defining the area (ROI)
    y1, y2 = max(0, cy-size), min(h_img, cy+size)
    x1, x2 = max(0, cx-size), min(w_img, cx+size)
    roi = img_hsv[y1:y2, x1:x2]
    
    # Calculate the channels H, S e V
    avg = cv2.mean(roi)
    return int(avg[0]), int(avg[1]), int(avg[2])

def find_squares(image_path):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or unable to load.")
    
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Here we apply filters (Gray and Blur)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    # Edge detection and finding contours
    low, high = get_adaptive_canny(gray)
    edges = cv2.Canny(blurred, low, high)
    #This helps to close gaps in edges
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # visão dos contornos do quadrado
    cv2.imshow("Vision of (Canny)", edges)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    squares_detected = []
    centers = []
    final_centers = []
    h_img, w_img = img.shape[:2]
    area_total = h_img * w_img  

    if hierarchy is not None:
        for cnt in contours:
            # Simplify to geometric shapes, it needs to have 4 sides and have 
            # proporcional sides = 1
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)

            if len(approx) == 4:
                area = cv2.contourArea(cnt)
                # Minimum area  
                if (area_total * 0.001) < area < (area_total * 0.20):
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect = float(w) / h
                    if 0.65 < aspect < 1.35:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])

                            is_duplicate = False
                            for (existing_cx, existing_cy) in centers:
                                # 25 pixels of tolerance because of duplicate
                                if np.sqrt((cx-existing_cx)**2 + (cy-existing_cy)**2) < 25:
                                    is_duplicate = True;
                                    break
                            
                            if not is_duplicate:
                                squares_detected.append(approx)
                                centers.append((cx, cy))
    
    sw, sh = 0, 0
    # in case we dont detect 9 squares, we use the cube contour
    if (len(squares_detected) == 1):
        contour_cube = squares_detected[0]
        x_cube, y_cube, w_cube, h_cube = cv2.boundingRect(contour_cube)
        final_centers = get_grid_points(squares_detected[0])
        sw, sh = w_cube // 3, h_cube // 3
        final_centers = sort_centers(final_centers)
    elif 4 <= len(squares_detected) < 9:
        print("Warning: Parcial detection. Inferring grade from stickers")
        # Create one big contourn with all the squares
        all_points = np.vstack(squares_detected)
        hull = cv2.convexHull(all_points)
        final_centers = get_grid_points(hull)
        x_h, y_h, w_h, h_h = cv2.boundingRect(hull)
        sw, sh = w_h // 3, h_h // 3
        final_centers = sort_centers(final_centers)
    elif len(centers) == 9:
        final_centers = sort_centers(centers)
        all_pts = np.vstack(squares_detected)
        x_all, y_all, w_all, h_all = cv2.boundingRect(all_pts)
        sw, sh = w_all // 3, h_all // 3
    else:
        print("Photo invalid. Take another one, be careful with light and background.")
        return
    
    margin_x = int(sw * 0.15)
    margin_y = int(sh * 0.15)
    # Here we show the squares detected in green
    for i, (cx, cy) in enumerate(final_centers):
        # Here we use a size fixe base in the area 
        if sw == 0:
            x, y, w, h = cv2.boundingRect(squares_detected[i])
            cv2.drawContours(img, [squares_detected[i]], -1, (0, 255, 0), 3)
            hue, sat, val = get_average_hsv(img_hsv, cx, cy)
            color_name = get_color_name(hue, sat, val)
            cv2.putText(img, str(i), (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(img, color_name, (x + 10, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
        else:
            # Drawing the gride
            pt1 = (cx - sw//2 + margin_x, cy - sh//2 + margin_y)
            pt2 = (cx + sw//2 - margin_x, cy + sh//2 - margin_y)
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 3)
            hue, sat, val = get_average_hsv(img_hsv, cx, cy)
            color_name = get_color_name(hue, sat, val)
            cv2.putText(img, str(i), (cx - 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(img, color_name, (cx - 30, cy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)


    # WIndow for the user to verify, possibliy to resize the window
    window_name = "Cube Face Verification " 
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    screen_width = 800
    h, w = img.shape[:2]
    scale = screen_width / w
    screen_height = int(h * scale)
    cv2.resizeWindow(window_name, screen_width, screen_height)
    cv2.moveWindow(window_name, 400, 100)

    print(f"Total stickers finded: {len(squares_detected)}")
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    lista_cores_face = []
    for i, (cx, cy) in enumerate(final_centers):
        h, s, v = get_average_hsv(img_hsv, cx, cy)
        lista_cores_face.append(get_color_name(h, s, v))

    return lista_cores_face  

if __name__ == "__main__":
    #teste de uma face do cubo
    path = input("Enter the image path for face U: .jpeg or .jpg:)\n")
    find_squares(path)