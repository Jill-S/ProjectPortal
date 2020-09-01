import React from "react";
import { NotificationManager } from "react-notifications";
import { Route, Link } from "react-router-dom";
import GuideHeader from "./GuideHeader";
import axios from "../../axios";
import Loading from "../shared/Loading";

export default class GuideRequest extends React.Component {
  constructor(props) {
    super(props);
    this.requests = [];
    this.state = {
      status: "",
      loading: true,
    };
  }
  componentDidMount() {
    axios
      .get("guideRequest/")
      .then(({ data }) => {
        this.requests = data;
        console.log(this.requests);
        this.setState({ loading: false });
      })
      .catch((err) => this.props.history.goBack());
  }

  render() {
    if (this.state.loading) return <Loading />;
    return (
      <>
        <Route component={GuideHeader} />
        <div className='guide-requests mx-auto' style={{ width: "90%" }}>
          <br />
          <div
            className='p-2 text-center shadow-sm rounded font-weight-bold  mx-auto'
            style={{
              color: "rgb(183, 32, 46)",
              fontSize: "1.1em",
              backgroundColor: "rgba(231, 231, 231, 0.459)",
            }}>
            Approval Requests
          </div>
          <br />
          {this.requests.length
            ? this.requests.map((request) => (
                <div id='card' className='slide-in-bottom'>
                  <div className='card shadow-sm my-4'>
                    <div className='card-header'>
                      <b>Group Id :</b> {request.team}
                    </div>
                    <div className='card-body'>
                      <div className='d-flex flex-md-row flex-column justify-content-between py-1'>
                        <div className='col d-flex  m-0 p-0'>
                          <b>Sent on : </b>
                          <div className='pl-2'>
                            {request.timestamp_requested}
                          </div>
                        </div>
                        <div className='col d-flex justify-content-between m-0 p-0 px-xl-5'>
                          <Link to={`/group/${request.team}`}>
                            <div className='text-primary'>
                              View Group Details
                            </div>
                          </Link>
                        </div>
                      </div>
                      <div className='d-flex flex-md-row flex-column  justify-content-start'>
                        <button
                          type='button'
                          class='btn btn-outline-success my-1 mr-3'
                          onClick={() => {
                            let res = window.confirm("Confirm accept");
                            if (res) {
                              axios
                                .post("acceptRequest/", {
                                  team_id: request.team,
                                })
                                .then(({ data }) => {
                                  NotificationManager.success(data);
                                  this.setState(
                                    { ...this.state },
                                    this.componentDidMount(),
                                  );
                                })
                                .catch((err) => {
                                  NotificationManager.error(err.response.data);
                                  this.setState(
                                    { ...this.state },
                                    this.componentDidMount(),
                                  );
                                });
                            }
                          }}>
                          Accept
                        </button>
                        <button
                          type='button'
                          class='btn btn-outline-danger my-1 mr-3'
                          onClick={() => {
                            let res = window.confirm("Confirm reject");
                            if (res) {
                              axios
                                .post("rejectRequest/", {
                                  team_id: request.team,
                                })
                                .then(({ data }) => {
                                  NotificationManager.error(data);
                                  this.setState(
                                    { ...this.state },
                                    this.componentDidMount(),
                                  );
                                })
                                .catch((err) => {
                                  NotificationManager.error(err.response.data);
                                  this.setState(
                                    { ...this.state },
                                    this.componentDidMount(),
                                  );
                                });
                            }
                          }}>
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            : "No requests"}
        </div>
      </>
    );
  }
}
