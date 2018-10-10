package main

import "github.com/astaxie/beego"
import "./controllers"

func main(){
    beego.SetStaticPath("/static","/home/lichzhang/code/JKTW/server/web/static/" )
    beego.Router("/list", &controllers.ListController{})
    beego.Run()
}
