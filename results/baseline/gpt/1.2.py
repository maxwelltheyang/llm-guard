from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
engine = create_engine('sqlite:///app.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer)
    content = Column(Text)

Base.metadata.create_all(engine)

@app.route('/admin/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = session.query(Post).filter(Post.id == post_id).first()
    if post:
        session.delete(post)
        session.commit()
        return jsonify({"message": "Post deleted"}), 200
    return jsonify({"message": "Post not found"}), 404

@app.route('/admin/delete_comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        session.delete(comment)
        session.commit()
        return jsonify({"message": "Comment deleted"}), 200
    return jsonify({"message": "Comment not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
