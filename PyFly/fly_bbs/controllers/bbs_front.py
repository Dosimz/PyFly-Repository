from flask import Blueprint, render_template, session, jsonify, url_for, redirect
from fly_bbs import forms, utils
from bson import ObjectId
from datetime import datetime
from fly_bbs.extensions import mongo

bbs_index = Blueprint("index", __name__)

@bbs_index.route('/')
def index():
    if 'username' in session:
        username = session['username']
        print(username)
    else:
        user = None
    return render_template('base.html', username=username)


@bbs_index.route('/add', methods=['GET', 'POST'])
@bbs_index.route('/edit/<ObjectId:post_id>', methods=['GET', 'POST'])
def add(post_id=None):
    posts_form = forms.PostsForm()  
    if posts_form.is_submitted():
        if not posts_form.validate():
            return jsonify({'status': 50001, 'msg': str(posts_form.errors)})
        utils.verify_num(posts_form.vercode.data)
        # # 用户权限控制
        # user = current_user.user
        # if not user.get('is_active', False) or user.get('is_disabled', False):
        #     return jsonify(code_msg.USER_UN_ACTIVE_OR_DISABLED)
        # # 用户金币权限控制
        # user_coin = user.get('coin', 0)
        # if posts_form.reward.data > user_coin:
        #     return jsonify(models.R.ok('悬赏金币不能大于拥有的金币，当前账号金币为：' + str(user_coin)))
        # 帖子信息
        posts = {
            'title': posts_form.title.data,
            'catalog_id': ObjectId(posts_form.catalog_id.data),
            # 'is_closed': False,
            'content': posts_form.content.data,
        }

        post_index = posts.copy()
        post_index['catalog_id'] = str(posts['catalog_id'])

        msg = '发帖成功！'
        # reward = posts_form.reward.data
        if post_id:
            posts['modify_at'] = datetime.now()
            mongo.db.posts.update_one({'_id': post_id}, {'$set': posts})
            msg = '修改成功！'

        else:
            posts['create_at'] = datetime.utcnow()
            # posts['reward'] = reward
            # posts['user_id'] = user['_id']
            # # 扣除用户发帖悬赏
            # if reward > 0:
            #     mongo.db.users.update_one({'_id': user['_id']}, {'$inc': {'coin': -reward}})
            mongo.db.posts.save(posts)
            post_id = posts['_id']

        # 更新索引文档
        # update_index(mongo.db.posts.find_one_or_404({'_id': post_id}))

        return redirect(url_for('index.index'))
    else:
        ver_code = utils.gen_verify_num()
        # session['ver_code'] = ver_code['answer']
        posts = None
        if post_id:
            posts = mongo.db.posts.find_one_or_404({'_id': post_id})
        title = '发帖' if post_id is None else '编辑帖子'
        return render_template('jie/add.html', page_name='jie', ver_code=ver_code['question'], form=posts_form, is_add=(post_id is None), post=posts, title=title)
