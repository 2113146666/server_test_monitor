package main

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"study/logger"
)

// import "study/logger"

// 1.1 Hello, World

// 打印hello, world
/*
import(
	"fmt"
)

func main() {
	fmt.Println("hello, world")
}
*/

// 1.2 命令行参数

// 实现echo

// func main() {
// 	var s, sep string
// 	for i := 1; i < len(os.Args); i++ {
// 		s += sep + os.Args[i]
// 		sep = " "
// 	}
// 	fmt.Println(s)

// 	// for initialization; condition; post {
// 	// 	// zero or more statements
// 	// }

// 	// for condition {
// 	// 	// ...
// 	// }

// 	// for {
// 	// 	// ...
// 	// }
// }

// func main() {
// 	s, sep := "", ""
// 	for _, arg := range os.Args[1:] {
// 		s += sep + arg
// 		sep = " "
// 	}
// }

/*
s := ""
短变量声明, 只能用于函数内部, 不能用于包变量 ???
var s string
字符串的默认初始化零值机制, 被初始化为""
var s = ""
一般用于同时初始化多个变量
var s string = ""
显式的标明变量类型
*/

// import (
// 	"fmt"
// 	"os"
// 	"strings"
// )

// func main() {
// 	// s := ""
// 	// var s string
// 	s := strings.Join(os.Args[1:], " ")
// 	fmt.Println(s)

// 	fmt.Println(os.Args[1:])
// }

// 1.3 查找重复的行
// 模拟dup命令

// import (
// 	"bufio"
// 	"fmt"
// 	"os"
// )

// func main() {
// 	counts := make(map[string]int)
// 	input := bufio.NewScanner(os.Stdin)
// 	for input.Scan() {
// 		input_text := input.Text()
// 		if input_text == "" {
// 			break
// 		}
// 		counts[input_text]++
// 	}

// 	for line, n := range counts {
// 		if n > 1 {
// 			fmt.Printf("%d\t%s\n", n, line)
// 		}
// 	}
// }

// %d          十进制整数
// %x, %o, %b  十六进制，八进制，二进制整数。
// %f, %g, %e  浮点数： 3.141593 3.141592653589793 3.141593e+00
// %t          布尔：true或false
// %c          字符（rune） (Unicode码点)
// %s          字符串
// %q          带双引号的字符串"abc"或带单引号的字符'c'
// %v          变量的自然形式（natural format）
// %T          变量的类型
// %%          字面上的百分号标志（无操作数）
// import (
// 	"study/logline"
// )

// type reload struct {
// 	times    int
// 	fileName []string
// }

// func countLines(f *os.File, fName string, counts map[string]reload) {
// 	input := bufio.NewScanner(f)
// 	for input.Scan() {
// 		text := input.Text()
// 		if text == "" {
// 			break
// 		}
// 		if count, exists := counts[text]; exists {
// 			_sign := true
// 			count.times++
// 			for _, _file := range count.fileName {
// 				if _file == fName {
// 					_sign = false
// 					continue
// 				}
// 			}
// 			if _sign {
// 				count.fileName = append(count.fileName, fName)
// 			}
// 			counts[text] = count
// 		} else {
// 			counts[text] = reload{times: 1, fileName: []string{fName}}
// 		}
// 	}
// }

// func searchRepeatLine() {
// 	counts := make(map[string]reload)
// 	files := os.Args[1:]
// 	if len(files) == 0 {
// 		countLines(os.Stdin, "input", counts)
// 		return
// 	}

// 	for _, arg := range files {
// 		f, err := os.Open(arg)
// 		if err != nil {
// 			fmt.Fprintf(os.Stderr, "dup: %v\n", err)
// 			continue
// 		}
// 		countLines(f, arg, counts)
// 		f.Close()
// 	}

// 	for content, numAndFileName := range counts {
// 		// logger.LogConsole(content, numAndFileName.times, numAndFileName.fileName)
// 		if numAndFileName.times > 1 {
// 			logger.LogConsole(content, numAndFileName.fileName)
// 		}
// 	}
// }

// 1.4 GIF动画

// var palette = []color.Color{color.White, color.Black} // 定义黑白两色的切片 slice

// const (
// 	whiteIndex = 0 // first color in palette
// 	blackIndex = 1 // next color in palette
// )

// func runGIF(out io.Writer) {
// 	const (
// 		cycles  = 5     // number of complete x oscillator revolutions
// 		res     = 0.001 // angular resolution
// 		size    = 100   // image canvas covers [-size..+size]
// 		nframes = 64    // 循环次数
// 		delay   = 8     // delay between frames in 10ms units
// 	)

// 	freq := rand.Float64() * 3.0        // 生成0 - 3.0的随机数
// 	anim := gif.GIF{LoopCount: nframes} // 定义一个gif结构类型, 循环次数置为64
// 	phase := 0.0

// 	for i := 0; i < nframes; i++ {
// 		rect := image.Rect(0, 0, 2*size+1, 2*size+1) // 创建一个矩形区域, 长宽都为 2 * 100 + 1
// 		img := image.NewPaletted(rect, palette)      // 创建一个在矩形区域内使用调色板的图像
// 		for t := 0.0; t < cycles*2*math.Pi; t += res {
// 			x := math.Sin(t)
// 			y := math.Sin(t*freq + phase)
// 			img.SetColorIndex(size+int(x*size+0.5), size+int(y*size+0.5),
// 				blackIndex)
// 		}
// 		phase += 0.1
// 		anim.Delay = append(anim.Delay, delay)
// 		anim.Image = append(anim.Image, img)
// 	}
// 	gif.EncodeAll(out, &anim) // NOTE: ignoring encoding errors
// }

// 1.5 获取 URL

func getUrl(addr string) {
	// resp, err := io.Copy(http.Get(addr)[0].Body, os.Stdout)
	// if err != nil {
	// 	logger.LogConsole("failed, reason is :", err)
	// 	return
	// }

	// fmt.Printf("%s", os.Stdout)
	// fmt.Printf("%s", resp)

	if !strings.HasPrefix(addr, "http://") {
		addr = "http://" + addr
	}
	logger.LogConsole(addr)

	resp, err := http.Get(addr)
	logger.LogConsole(resp.Status)
	if err != nil {
		logger.LogConsole("failed, reason is :", err)
		return
	}
	defer resp.Body.Close()

	// _, err = io.Copy(os.Stdout, resp.Body)

	if err != nil {
		logger.LogConsole("failed, reason is :", err)
		return
	}

	// // logger.LogConsole(bi)
	// fmt.Printf("%s", os.Stdout)
}

func main() {
	for _, url := range os.Args[1:] {
		getUrl(url)
	}

	defer tearDown()
}

// main函数执行结束的收尾函数
func tearDown() {
	// 捕捉panic错误
	printError()

	// 关闭日志文件的写入
	logger.CloseLogFile()
}

// 捕捉panic错误
func printError() {
	if r := recover(); r != nil {
		fmt.Println("Recovered from panic:", r)
	}
}
