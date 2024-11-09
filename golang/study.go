package main

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

import (
	"fmt"
	"os"
	"strings"
)

func main() {
	// s := ""
	// var s string
	s := strings.Join(os.Args[1:], " ")
	fmt.Println(s)

	fmt.Println(os.Args[1:])
}
