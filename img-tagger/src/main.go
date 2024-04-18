package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	"io"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/fogleman/gg"
	"github.com/google/uuid"
	"golang.org/x/image/draw"

	"github.com/minio/minio-go"
)

// ----------------------------------------------------
type appStatus struct {
	Timestamp time.Time `json:"timestamp"`
	Hostname  string    `json:"hostname"`
	Message   string    `json:"message"`
}

type uploadResponse struct {
	Filename  string `json:"filename"`
	Filesize  int64  `json:"filesize"`
	Timestamp string `json:"timestamp"`
}

// ----------------------------------------------------
func create_minio_config() map[string]string {
	minio_config := map[string]string{
		"MINIO_ENDPOINT":   "localhost",
		"MINIO_USE_SSL":    "true",
		"MINIO_ACCESS_KEY": "",
		"MINIO_SECRET_KEY": "",
		"MINIO_BUCKET":     "img-tagger",
		"MINIO_REGION":     "local",
	}

	for key, _ := range minio_config {
		if os.Getenv(key) != "" {
			minio_config[key] = os.Getenv(key)
		}
	}
	return minio_config
}

var font_filepath string = "./AppFont.ttf"

// var font_url string = "https://get.fontspace.co/download/font/MVZx/Nzk0ZTEzZDc3MzQwNDNlODhhM2FlNDdhZmUwNGRjZDYudHRm/BodoniflfBold-MVZx.ttf"
var font_url string = "https://get.fontspace.co/download/font/3zOvZ/Yzc2MTk1ZWFmNWYyNDE4NWJiNTE2MWJiMDVjZjFjNGQudHRm/MontserratBlack-3zOvZ.ttf"

// ----------------------------
func AppStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	hostname, _ := os.Hostname()
	status_object := appStatus{
		Timestamp: time.Now(),
		Hostname:  hostname,
		Message:   "Hello World",
	}
	jsonData, _ := json.Marshal(status_object)
	fmt.Fprint(w, string(jsonData))
}

// ----------------------------
func download_app_font() error {
	if os.Getenv("FONT_URL") != "" {
		font_url = os.Getenv("FONT_URL")
	}
	out, err := os.Create(font_filepath)
	if err != nil {
		return err
	}
	defer out.Close()
	resp, err := http.Get(font_url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("bad status: %s", resp.Status)
	}
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}
	return nil
}

// ----------------------------
func ToStdJpeg(img image.Image) ([]byte, error) {
	buf := new(bytes.Buffer)
	jpegOtions := jpeg.Options{
		Quality: 90,
	}
	//------------
	if err := jpeg.Encode(buf, img, &jpegOtions); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

// ----------------------------
func draw_meta_in_img(imageBytes []byte, filename string) (image.Image, error) {
	bgImage, _, err := image.Decode(bytes.NewReader(imageBytes))
	if err != nil {
		return nil, err
	}

	//------------
	sb := bgImage.Bounds()
	nh := 1400 * sb.Dy() / sb.Dx()
	dst := image.NewRGBA(image.Rect(0, 0, 1400, nh))
	draw.BiLinear.Scale(dst, dst.Bounds(), bgImage, sb, draw.Over, nil)

	//------------
	imgWidth := dst.Bounds().Dx()
	imgHeight := dst.Bounds().Dy()
	dc := gg.NewContext(imgWidth, imgHeight)
	dc.DrawImage(dst, 0, 0)
	dc.LoadFontFace(font_filepath, 40)
	dc.SetColor(color.Black)

	//------------
	t := time.Now()
	time_str := fmt.Sprintf("Timestamp: %s", t.Format("2006-01-02 15:04:05"))
	size_str := fmt.Sprintf("Size: %d", len(imageBytes))
	file_str := fmt.Sprintf("Filename: %s", filename)
	dc.DrawString(time_str, 50.0, 80.0)
	dc.DrawString(size_str, 50.0, 130.0)
	dc.DrawString(file_str, 50.0, 180.0)

	//------------
	return dc.Image(), nil
}

// ----------------------------
func save_on_minio(img_data []byte) error {
	mc := create_minio_config()
	use_ssl, _ := strconv.ParseBool(mc["MINIO_USE_SSL"])
	minio_client, err := minio.New(mc["MINIO_ENDPOINT"], mc["MINIO_ACCESS_KEY"], mc["MINIO_SECRET_KEY"], use_ssl)
	if err != nil {
		fmt.Println(err)
		return err
	}
	exists, err := minio_client.BucketExists(mc["MINIO_BUCKET"])
	if err != nil {
		fmt.Println(err)
		return err
	}
	if !exists {
		err = minio_client.MakeBucket(mc["MINIO_BUCKET"], mc["MINIO_REGION"])
		if err != nil {
			fmt.Println(err)
			return err
		}
	}
	obj_name := uuid.New().String() + ".jpeg"
	reader := bytes.NewReader(img_data)
	n, err := minio_client.PutObject(
		mc["MINIO_BUCKET"],
		obj_name,
		reader,
		reader.Size(),
		minio.PutObjectOptions{ContentType: "application/octet-stream"},
	)
	if err != nil {
		fmt.Println(err)
		return err
	}
	fmt.Println("Uploaded", obj_name, " of size: ", n, "Successfully.")
	return nil
}

// ----------------------------
func Handler(w http.ResponseWriter, r *http.Request) {
	download_app_font()
	w.Header().Set("Content-Type", "application/json")

	//------------
	file, handler, err := r.FormFile("image")
	if err != nil {
		fmt.Println(err)
	}
	defer file.Close()

	//------------
	imageBytes, err := io.ReadAll(file)
	if err != nil {
		fmt.Println(err)
	}

	taggedImageBytes, _ := draw_meta_in_img(imageBytes, handler.Filename)
	convertedImageBytes, _ := ToStdJpeg(taggedImageBytes)
	save_on_minio(convertedImageBytes)

	// tempFile, err := os.CreateTemp("temp-images", "upload-*.jpg")
	// if err != nil {
	// 	fmt.Println(err)
	// }
	// defer tempFile.Close()
	// tempFile.Write(convertedImageBytes)

	//------------
	res := uploadResponse{
		Filename:  handler.Filename,
		Filesize:  handler.Size,
		Timestamp: time.Now().String(),
	}
	jsonData, err := json.Marshal(res)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Fprint(w, string(jsonData))
}

// ----------------------------------------------------
func setupRoutes() {
	http.HandleFunc("/", AppStatus)
	http.HandleFunc("/upload", Handler)
	http.ListenAndServe(":8080", nil)
}

func main() {
	download_app_font()
	fmt.Println("Start Image Tagger App @ :8080")
	setupRoutes()
}
