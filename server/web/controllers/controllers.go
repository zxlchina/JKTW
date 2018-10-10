package controllers

import (
        //"container/list"
        "github.com/astaxie/beego"
        "database/sql"
        _ "github.com/go-sql-driver/mysql"
        "encoding/json"
        //"github.com/bitly/go-simplejson"
        "fmt"
        "strconv"
        //"time"
       )

type ListController struct {
    beego.Controller
}


type ContentInfo struct {
    Id string `json:"id"`
    Title string `json:"title"`
    Data []string `json:"data"`
    Create_time string `json:create_time`
    Last_up_time  string `json:last_up_time`
    State int `json:state`
    HeadImg string `json:head_img`
}

type SData struct {
    Data []string `json:data`
}


func (this *ListController) Get() {
    //this.Ctx.WriteString("Hello World") 
    //从数据库中读取文章列表
    db, err := sql.Open("mysql", "root:zxlchina@tcp(127.0.0.1:3306)/jktw")
    if err != nil {
        this.Data["json"] = map[string]interface{}{"success": -1, "message": "database connect error!"}
        this.ServeJSON() 
        return 
    }

    var page_index int = 0
    var page_size int = 15

    if this.GetString("page_index") != "" {
        page_index, _ = strconv.Atoi(this.GetString("page_index"))
    }

    if this.GetString("page_size") != "" {
        page_size, _ = strconv.Atoi(this.GetString("page_size"))
    }

    if (page_size > 50){
        page_size = 50
    }



    var sql_str string
    sql_str = fmt.Sprintf("select cid, title, sdata, create_time, last_up_time, state, head_img  from content_info where voice_state = 1 order by create_time desc limit %d,%d", page_index * page_size, page_size)
    //下面开始处理数据
    rows, err := db.Query(sql_str)
    defer rows.Close() 

    if  err != nil {
        this.Data["json"] = map[string]interface{}{"success": -2, "message": "query error!"}
        this.ServeJSON() 
        return 
    }

    //组装数据
    var nums []ContentInfo
    for rows.Next() {
        var item ContentInfo
        var create_time sql.NullString
        var last_up_time sql.NullString
        var sdata_str sql.NullString
        var head_img sql.NullString

        err := rows.Scan(&item.Id, &item.Title, &sdata_str, &create_time, &last_up_time, &item.State, &head_img)
        
        if create_time.Valid {
            //item.Create_time, _ = time.Parse("2006-01-02 15:04:05", create_time.String)
            item.Create_time = create_time.String
        }

        if last_up_time.Valid {
            //item.Last_up_time, _ = time.Parse("2006-01-02 15:04:05", last_up_time.String)
            item.Last_up_time = last_up_time.String
        }

        if head_img.Valid {
            item.HeadImg = head_img.String
        }


        //解析sdata数据，填入item.Data
        var sdata SData 
        err = json.Unmarshal([]byte(sdata_str.String), &sdata)
        if err != nil {
            fmt.Println("Unmarshal Error")
            continue 
        }

        //赋值
        item.Data = sdata.Data
        
        body, err := json.Marshal(item)
        if err != nil {
            this.Data["json"] = map[string]interface{}{"success": -2, "message": "json error !"}
            this.ServeJSON() 
            return 
        }

        fmt.Println(string(body[:]))

        nums = append(nums, item)
    }
    //nums := [...]int {1, 2, 3}


    this.Data["json"] = map[string]interface{}{"success": 0, "message": "111", "list": nums, "count": len(nums)}
    this.ServeJSON()
}
