package main

import "github.com/astaxie/beego"
import "./controllers"

func main(){
    static_path := beego.AppConfig.String("static_path")
    beego.SetStaticPath("/static", static_path)
    beego.Router("/list", &controllers.ListController{})
    beego.Run()
}
