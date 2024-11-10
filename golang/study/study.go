package main

import (
	"bufio"
	"fmt"
	"os"
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

type reload struct {
	times    int
	fileName []string
}

func countLines(f *os.File, fName string, counts map[string]reload) {
	input := bufio.NewScanner(f)
	for input.Scan() {
		text := input.Text()
		if text == "" {
			break
		}
		if count, exists := counts[text]; exists {
			_sign := true
			count.times++
			for _, _file := range count.fileName {
				if _file == fName {
					_sign = false
					continue
				}
			}
			if _sign {
				count.fileName = append(count.fileName, fName)
			}
			counts[text] = count
		} else {
			counts[text] = reload{times: 1, fileName: []string{fName}}
		}
	}
}

func searchRepeatLine() {
	counts := make(map[string]reload)
	files := os.Args[1:]
	if len(files) == 0 {
		countLines(os.Stdin, "input", counts)
		return
	}

	for _, arg := range files {
		f, err := os.Open(arg)
		if err != nil {
			fmt.Fprintf(os.Stderr, "dup: %v\n", err)
			continue
		}
		countLines(f, arg, counts)
		f.Close()
	}

	for content, numAndFileName := range counts {
		// logger.LogConsole(content, numAndFileName.times, numAndFileName.fileName)
		if numAndFileName.times > 1 {
			logger.LogConsole(content, numAndFileName.fileName)
		}
	}
}

func main() {
	searchRepeatLine()

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
