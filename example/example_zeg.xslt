<svg width="256" height="256" version="1.1" viewBox="0 0 67.733332 67.733335" xmlns="http://www.w3.org/2000/svg" xmlns:xsl = "http://www.w3.org/1999/XSL/Transform" xsl:version="1.0">
  <xsl:variable name="key_small" select="/row/value[@colname='Market Segment']"/>
  <xsl:variable name="key_medium" select="/row/value[@colname='Market Segment']"/>
  <xsl:variable name="key_large" select="/row/value[@colname='Market Segment']"/>
 <g transform="translate(0 -229.27)">
  <g>
   <!-- background colour based on Market Segment -->
   <xsl:choose>
    <xsl:when test="$key_small = 'Small'">
        <rect y="229.27" width="67.733" height="67.733" fill="#a6bddb"/>
    </xsl:when>
    <xsl:when test="$key_small = 'Medium'">
        <rect y="229.27" width="67.733" height="67.733" fill="#74a9cf"/>
    </xsl:when>
    <xsl:when test="$key_small = 'Large'">
        <rect y="229.27" width="67.733" height="67.733" fill="#0570b0"/>
    </xsl:when>
    <xsl:when test="$key_small = 'Top 10'">
        <rect y="229.27" width="67.733" height="67.733" fill="#023858"/>
    </xsl:when>
    <xsl:otherwise>
      <rect y="229.27" width="67.733" height="67.733" fill="#a6bddb"/>
    </xsl:otherwise>
  </xsl:choose>
  </g>
 </g>
</svg>
