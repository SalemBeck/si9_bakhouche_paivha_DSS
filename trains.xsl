<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="UTF-8"/>

<xsl:key name="station-by-id" match="station" use="@id"/>

<xsl:template match="/">
<html>
<head>
  <meta charset="UTF-8"/>
  <title>Train Trips Report</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f5f5f5;
      padding: 20px;
      color: #333;
    }
    h1 {
      text-align: center;
      color: #c0392b;
      margin-bottom: 30px;
    }
    .note {
      text-align: center;
      font-size: 0.85em;
      color: #888;
      margin-bottom: 20px;
    }
    .line-section {
      background: white;
      margin-bottom: 25px;
      padding: 15px 20px;
      border-left: 5px solid #2c3e50;
    }
    .line-title {
      font-size: 1.1em;
      font-weight: bold;
      color: #2c3e50;
      border-bottom: 1px solid #ddd;
      padding-bottom: 8px;
      margin-bottom: 12px;
    }
    .line-title span { color: #c0392b; }
    .trip-label { font-weight: bold; margin: 12px 0 6px; font-size: 0.95em; }
    .trip-label span { color: #c0392b; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 5px; }
    th { background: #2c3e50; color: white; padding: 7px 12px; text-align: center; }
    td { padding: 7px 12px; border-bottom: 1px solid #eee; text-align: center; }
    tr:nth-child(even) { background: #f9f9f9; }
    .vip { color: #c0392b; font-weight: bold; }
    .days { font-size: 0.82em; color: #888; margin-bottom: 6px; font-style: italic; }
  </style>
</head>
<body>

<p class="note">TP_Do not copy directly / This page is implemented by the student : ... name ... / Group : ...</p>
<h1>Train Trips Report</h1>

<xsl:apply-templates select="transport/lines/line"/>

</body>
</html>
</xsl:template>

<xsl:template match="line">
  <xsl:variable name="dep" select="key('station-by-id', @departure)/@name"/>
  <xsl:variable name="arr" select="key('station-by-id', @arrival)/@name"/>
  <div class="line-section">
    <div class="line-title">
      Line: <xsl:value-of select="@code"/> (
      <span><xsl:value-of select="$dep"/></span>
      -&gt;
      <span><xsl:value-of select="$arr"/></span>
      )
    </div>
    <b>Detailed List of Trips:</b>
    <xsl:apply-templates select="trips/trip">
      <xsl:with-param name="dep" select="$dep"/>
      <xsl:with-param name="arr" select="$arr"/>
    </xsl:apply-templates>
  </div>
</xsl:template>

<xsl:template match="trip">
  <xsl:param name="dep"/>
  <xsl:param name="arr"/>
  <div class="trip-label">
    Trip No. <xsl:value-of select="@code"/>:
    Departure: <span><xsl:value-of select="$dep"/></span>
    | Arrival: <span><xsl:value-of select="$arr"/></span>
  </div>
  <div class="days">Days: <xsl:value-of select="days"/></div>
  <table>
    <thead>
      <tr>
        <th>Schedule</th>
        <th>Train Type</th>
        <th>Class</th>
        <th>Price (DA)</th>
      </tr>
    </thead>
    <tbody>
      <xsl:apply-templates select="class">
        <xsl:with-param name="train_type" select="@type"/>
        <xsl:with-param name="dep_time" select="schedule/@departure"/>
        <xsl:with-param name="arr_time" select="schedule/@arrival"/>
      </xsl:apply-templates>
    </tbody>
  </table>
</xsl:template>

<xsl:template match="class">
  <xsl:param name="train_type"/>
  <xsl:param name="dep_time"/>
  <xsl:param name="arr_time"/>
  <tr>
    <td><xsl:value-of select="$dep_time"/> - <xsl:value-of select="$arr_time"/></td>
    <td><xsl:value-of select="$train_type"/></td>
    <td>
      <xsl:choose>
        <xsl:when test="@type='VIP'">
          <span class="vip">VIP</span>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@type"/>
        </xsl:otherwise>
      </xsl:choose>
    </td>
    <td>
      <xsl:choose>
        <xsl:when test="@type='VIP'">
          <span class="vip"><xsl:value-of select="@price"/></span>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="@price"/>
        </xsl:otherwise>
      </xsl:choose>
    </td>
  </tr>
</xsl:template>

</xsl:stylesheet>
