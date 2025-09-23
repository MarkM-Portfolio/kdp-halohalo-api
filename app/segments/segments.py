from . import segments_api
from flask import request
from flask import current_app
from app.extensions import mongo as mongo_ext
import time
import pandas as pd
import json
from bson import json_util
from os import environ
from kumuniverse.logger import Logger

logger = Logger(name="halohalo", env=environ.get("ENV"))

def update_segment_stats(segment_name, flag, count):
    mongo_stats = mongo_ext.get_segp_client()
    segment_stats_collection = current_app.config["SEGMENTS_STATS_COLLECTION"]
    segmentation_db_for_stats = current_app.config["SEGP_DB"]
    last_updated = int(time.time())

    try:
        if flag == "new":
            mongo_stats.client[segmentation_db_for_stats][segment_stats_collection].update_one(
                {"segment_name": segment_name},
                {
                    "$inc": {"active": int(count), "total":int(count)},
                    "$set": {"last_updated": last_updated},
                },
                True
            )
        elif flag == "activate":
            mongo_stats.client[segmentation_db_for_stats][segment_stats_collection].update_one(
                {"segment_name": segment_name},
                {
                    "$inc": {"active": int(count), "inactive": int(-count)},
                    "$set": {"last_updated": last_updated},
                },
                True
            )
        else:
            mongo_stats.client[segmentation_db_for_stats][segment_stats_collection].update_one(
                {"segment_name": segment_name},
                {
                    "$inc": {"active": int(-count), "inactive": int(count)},
                    "$set": {"last_updated": last_updated},
                },
                True
            )
        logger.info(msg = f"Updated segment stats for segment {segment_name}")
        return f"Updated segment stats for segment {segment_name}"

    except Exception:
        logger.error(
            msg="Failed segment stats update for {segment_name} with flag {flag}"
        )

@segments_api.route("/health", methods=["GET", "POST"])
def test():
    #test comment
    logger.info(msg="Health: segments health check")
    return "/segments health check"


@segments_api.route("/all_segments", methods=["GET"])
def get_all_segments():
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]
    data = mongo.client[segmentation_db][segments_collection].distinct("segment_name")

    item_list = []
    for item in data:
       item_list.append(item)

    return {"status": 200, "data": item_list}


@segments_api.route("", methods=["GET"])
def segments():
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]
    # data = mongo.client[segmentation_db][segments_collection].distinct("segment_name")

    data = mongo.client[segmentation_db][segments_collection].aggregate(
        [
            {"$match": {"is_member": True}},
            {"$group": {"_id": "$segment_name", "count": {"$count": {}}}},
            {"$sort": {"count": -1}},
        ]
    )

    item_list = []
    for item in data:
        item_list.append(item)

    return {"status": 200, "data": item_list}


@segments_api.route("<segment_name>", methods=["GET"])
def segment(segment_name):
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    data = {}
    query = {"segment_name": segment_name, "is_member": True}
    segment_count = mongo.client[segmentation_db][segments_collection].count_documents(
        query
    )
    data["total_users"] = segment_count

    return {"status": 200, "data": data}


@segments_api.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    query = {"user_id": user_id}
    data = mongo.get_items(segmentation_db, segments_collection, query)

    return json.loads(json_util.dumps(dict(enumerate(data))))


@segments_api.route("/users", methods=["POST"])
def add_user():
    # add user to segment
    mongo = mongo_ext.get_segp_client()
    user_id = request.json["user_id"]
    segment_name = request.json["segment_name"]

    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    query = {"user_id": user_id, "segment_name": segment_name}
    data = mongo.get_items(segmentation_db, segments_collection, query)

    if data:
        # list is not empty
        logger.error(
            msg="Add User: Duplicate entry. user_id and segment name already exist"
        )
        return {
            "status": 400,
            "error": "Duplicate entry. user_id and segment name already exist",
        }, 400
    else:
        timestamp = int(time.time())
        mongo.insert_item(
            database=segmentation_db,
            collection=segments_collection,
            query={
                "user_id": user_id,
                "segment_name": segment_name,
                "is_member": True,
                "created_at": timestamp,
                "updated_at": timestamp,
            },
        )
        update_segment_stats(segment_name, "new", 1)
        logger.info(msg="Add User: Successfully added user to segmentation database")
        return {
            "status": 200,
            "error": "Successfully added user to segmentation database",
        }, 200


@segments_api.route("/users/batch", methods=["POST"])
def add_users():
    # add user to segment
    mongo = mongo_ext.get_segp_client()
    batch_input = request.json["users"]
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    duplicate = []
    for i in batch_input:
        query = i
        data = mongo.get_items(segmentation_db, segments_collection, query)
        if data:
            duplicate.append(i)
        else:
            timestamp = int(time.time())
            i["is_member"] = True
            i["created_at"] = timestamp
            i["updated_at"] = timestamp

    if len(batch_input) > len(duplicate):
        if len(duplicate) > 1:
            message = "Duplicate entries were not inserted to the database"
        else:
            message = "There were no duplicate entries"
        batch_input = [ele for ele in batch_input if ele not in duplicate]
        mongo.insert_items(
            database=segmentation_db,
            collection=segments_collection,
            queries=batch_input,
        )
        # update segments stats
        unique_segment_name = set(list(map(lambda x: x["segment_name"] , batch_input)))
        for segment_name in unique_segment_name:
            count = int(len([x for x in batch_input if x["segment_name"] == segment_name]))
            update_segment_stats(segment_name, "new", count)
        logger.info(msg="Add User: Users successfully added to the database " + message)
        return {
            "status": 200,
            "message": "Users successfully added to the database " + message,
        }, 200
    else:
        logger.error(msg="Add Request: Request contains duplicate entries")
        return {
            "status": 400,
            "error": "Request contains duplicate entries",
        }, 400


@segments_api.route("/users/<user_id>/enable", methods=["PUT"])
def activate(user_id):
    # update user's segment status
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    # get _id of user_id provided
    segment_name = request.json["segment_name"]
    query = {"user_id": user_id, "segment_name": segment_name}
    data = mongo.get_items(segmentation_db, segments_collection, query)
    df = pd.DataFrame(data)
    item_id = df.iloc[0]["_id"]

    update_value = {"is_member": True, "updated_at": int(time.time())}
    old_status = df.iloc[0]["is_member"]
    mongo.update_item(
        database=segmentation_db, collection=segments_collection, id=item_id, value=update_value
    )
    # update segments stats only if new status != old status
    if old_status != True:
        update_segment_stats(segment_name, "activate", 1)
    logger.info(msg="Activate: Successfully enabled user for this segment")
    return {
        "status": 200,
        "error": "Successfully enabled user for this segment",
    }, 200


@segments_api.route("/users/<user_id>/disable", methods=["PUT"])
def deactivate(user_id):
    # update user's segment status
    mongo = mongo_ext.get_segp_client()
    segmentation_db = current_app.config["SEGP_DB"]
    segments_collection = current_app.config["SEGMENTS_COLLECTION"]

    # get _id of user_id provided
    segment_name = request.json["segment_name"]
    query = {"user_id": user_id, "segment_name": segment_name}
    data = mongo.get_items(segmentation_db, segments_collection, query)
    df = pd.DataFrame(data)
    item_id = df.iloc[0]["_id"]

    update_value = {"is_member": False, "updated_at": int(time.time())}
    old_status = df.iloc[0]["is_member"]
    mongo.update_item(
        database=segmentation_db, collection=segments_collection, id=item_id, value=update_value
    )
    # update segments stats only if new status != old status
    if old_status != False:
        update_segment_stats(segment_name, "deactivate", 1)
    logger.info(msg="Deactivate: Successfully disabled user for this segment")
    return {
        "status": 200,
        "error": "Successfully disabled user for this segment",
    }, 200
