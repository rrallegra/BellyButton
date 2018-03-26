
# import dependencies 
import json
from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, desc 


# Database Setup
engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite")

# Flask set up
app = Flask(__name__)


Base = automap_base()
Base.prepare(engine, reflect=True)

otu = Base.classes.otu
samples = Base.classes.samples
metadata_samples = Base.classes.samples_metadata

# Create Session 
session = Session(engine)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/names")
def names():
    sample_names = session.query(samples).statement
    df = pd.read_sql_query(sample_names, session.bind)
    df.set_index('otu_id', inplace=True)

    return jsonify(list(df.columns))

@app.route("/otu")
def otu():
    otu_query = session.query(otu.lowest_taxonomic_unit_found).all()
    otu_json = np.ravel(otu_query)

    return jsonify(list(otu_json))

@app.route('/samples/<sample>')
def sample_otu(sample):
    query = session.query(samples).statement
    otu_df = pd.read_sql_query(query, session.bind)

    otu_df = otu_df.sort_values(by=sample, ascending=0)

    data = [{
        "otu_ids": otu_df[sample].index.values.tolist(),
        "sample_values": otu_df[sample].values.tolist()
    }]

    return jsonify(data)


@app.route("/metadata/<sample>")
def metadata(sample):
    results = session.query(metadata_samples.AGE, metadata_samples.BBTYPE, metadata_samples.ETHNICITY, 
    metadata_samples.GENDER, metadata_samples.LOCATION, metadata_samples.SAMPLEID).filter(metadata_samples.SAMPLEID == sample).all()

    metadata_dict= {}
    for result in results: 
            metadata_dict["AGE"] = result[0]
            metadata_dict["BBTYPE"] = result[1]
            metadata_dict["ETHNICITY"] = result[2]
            metadata_dict["GENDER"] = result[3]
            metadata_dict["LOCATION"] =  result[4]
            metadata_dict["SAMPLEID"] = result[5]
        
    return jsonify(metadata_dict)

@app.route("/wfreq/<sample>")
def wfreq(sample):
    results = session.query(metadata_samples.WFREQ).filter(metadata_samples.SAMPLEID == sample).all()
    wfreq_int = results[0][0]

    return jsonify(wfreq_int)


if __name__ == "__main__":
    app.run(debug=True)
    




    