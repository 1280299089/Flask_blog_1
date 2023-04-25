# from model import *
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from decorators import login_limit
from werkzeug.utils import secure_filename
import uuid
import os
import time

blog = Blueprint("blog", __name__, url_prefix="/blog")
from model import *

# 写博客页面
@blog.route('/writeBlog', methods=['POST', 'GET'])
@login_limit
def writeblog():
    """写博客，博客表中会保存标题、博客内容、当前时间等字段。如下是写博客的视图函数。"""
    if request.method == 'GET':
        return render_template('writeBlog.html')
    if request.method == 'POST':
        title = request.form.get("title")
        text = request.form.get("text")
        username = session.get('username')
        # 获取当前系统时间
        create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        user = User.query.filter(User.username == username).first()
        blog = Blog(title=title,
                    text=text,
                    create_time=create_time,
                    user_id=user.id)
        db.session.add(blog)
        db.session.commit()
        blog = Blog.query.filter(Blog.create_time == create_time).first()
        return render_template('blogSuccess.html', title=title, id=blog.id)


# 上传图片
@blog.route('/imgUpload', methods=['POST'])
@login_limit
def imgUpload():
    """如下定义一个文件上传的视图函数(这里需要注意的是Markdown上传图片是使用的POST方法)"""
    try:
        # Flask接收Markdown上传图片的语句：
        file = request.files.get('editormd-image-file')
        fname = secure_filename(file.filename)
        ext = fname.rsplit('.')[-1]
        # 生成一个uuid作为文件名
        fileName = str(uuid.uuid4()) + "." + ext
        filePath = os.path.join("static/uploadImg/", fileName)
        file.save(filePath)
        return {'success': 1, 'message': '上传成功!', 'url': "/" + filePath}
    except Exception:
        return {'success': 0, 'message': '上传失败'}


# 博客详情页面
@blog.route('/showBlog/<id>')
def showBlog(id):
    # 在博客列表中点击博客的标题可以进入博客的详情页面，详情页面展示了博客的详细内容以及评论内容。
    blog = Blog.query.filter(Blog.id == id).first()
    comment = Comment.query.filter(Comment.blog_id == blog.id)
    return render_template("showBlog.html", blog=blog, comment=comment)


# 展示全部博客
@blog.route("/blogAll")
def blogAll():
    """查看博客列表就是遍历所有已发布的博客。先定义一个视图函数，查询所有已发布的博客，传递到前端进行遍历显示。视图函数代码如下："""
    # order_by按照时间倒序.因为最新发布的博客在数据库的最后一条，所以这里根据发布时间倒序查询。
    blogList = Blog.query.order_by(Blog.create_time.desc()).all()
    return render_template('blogAll.html', blogList=blogList)


# 博客修改
@blog.route("/update/<id>", methods=['POST', 'GET'])
@login_limit
def update(id):
    # 在我的博客中，有修改博客的链接，把当前的博客id当做参数传递到后台，查询当前这条博客的数据，进行修改。
    if request.method == 'GET':
        blog = Blog.query.filter(Blog.id == id).first()
        return render_template('updateBlog.html', blog=blog)
    if request.method == 'POST':
        id = request.form.get("id")
        title = request.form.get("title")
        text = request.form.get("text")
        blog = Blog.query.filter(Blog.id == id).first()
        blog.title = title
        blog.text = text
        # 但是这里是不是有小问题，修改后的博客，改正时间是没有更新的。或者说这里的博客在创建好后，时间就固定了。那么可以尝试去添加功能：最近的修改时间
        db.session.commit()
        return render_template('blogSuccess.html', title=title, id=id)


# 删除博客
@blog.route("/delete/<id>")
@login_limit
def delete(id):
    blog = Blog.query.filter(Blog.id == id).first()
    db.session.delete(blog)
    db.session.commit()
    return {'state': True, 'msg': "删除成功！"}


# 查看个人博客
@blog.route("/myBlog")
@login_limit
def myBlog():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    # order_by按照时间倒序
    blogList = Blog.query.filter(Blog.user_id == user.id).order_by(
        Blog.create_time.desc()).all()
    return render_template("myBlog.html", blogList=blogList)


# 评论
@blog.route("/comment", methods=['POST'])
@login_limit
def comment():
    text = request.values.get('text')
    blogId = request.values.get('blogId')  # 此处的blogid怎么来的？
    username = session.get('username')
    # 获取当前系统时间
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    user = User.query.filter(User.username == username).first()
    comment = Comment(text=text,
                      create_time=create_time,
                      blog_id=blogId,
                      user_id=user.id)
    db.session.add(comment)
    db.session.commit()
    return {
        'success': True,
        'message': '评论成功！',
    }


# 用户所有的评论
@blog.route('/myComment')
@login_limit
def myComment():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    # order_by按照时间倒序
    commentList = Comment.query.filter(Comment.user_id == user.id).order_by(
        Comment.create_time.desc()).all()
    return render_template("myComment.html", commentList=commentList)


# 删除评论
@blog.route('/deleteCom/<id>')
def deleteCom(id):
    com = Comment.query.filter(Comment.id == id).first()
    db.session.delete(com)
    db.session.commit()
    return {'state': True, 'msg': "删除成功！"}
